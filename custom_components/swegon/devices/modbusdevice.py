import logging

from enum import Enum
from homeassistant.helpers.entity import EntityCategory

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import ByteOrder, WordOrder, ModbusMode, ModbusPollMode
from .datatypes import ModbusDefaultGroups, ModbusGroup, ModbusDatapoint
from .datatypes import EntityDataSelect, EntityDataNumber
from .modbustraffic import ModbusTrafficStats
from ..busmanager import BusClient

import json
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

class ModbusDevice():
    # Default properties
    manufacturer = None
    model = None
    sw_version = None
    serial_number = None

    # Settings
    byte_order = ByteOrder.MSB
    word_order = WordOrder.NORMAL

    def __init__(self, client: BusClient):
        self._client = client
        self._slave_id = client.slave_id

        # Per-device traffic stats
        self.traffic = ModbusTrafficStats()

        # Register device stats with the bus
        self._client._bus.register_device(self._slave_id, self.traffic)

        self.Datapoints: dict[ModbusGroup, dict[str, ModbusDatapoint]] = {}
        self.loadDatapoints()
        self.loadConfigUI()
        _LOGGER.debug("Loaded datapoints for %s %s", self.manufacturer, self.model)

        self.firstRead = True

    def close(self):
        """Close the underlying client safely."""
        try:
            _LOGGER.debug("Shutting down and disconnecting device: %s %s",  self.manufacturer, self.model)
            self._client.close()
        except Exception as e:
            _LOGGER.warning("Error closing client for device %s %s: %s", self.manufacturer, self.model, e)
        finally:
            self._client = None

    def loadConfigUI(self):
        # Ensure default groups exist
        config_group = self.Datapoints.setdefault(ModbusDefaultGroups.CONFIG, {})
        ui_group = self.Datapoints.setdefault(ModbusDefaultGroups.UI, {})

        if not config_group: return  # Nothing to do if CONFIG is empty

        # Check if CONFIG group has any number or select datapoints
        has_number = any(isinstance(dp.entity_data, EntityDataNumber) for dp in config_group.values())
        has_select = any(isinstance(dp.entity_data, EntityDataSelect) for dp in config_group.values())

        if not (has_number or has_select): return   # No relevant datapoints, nothing to add

        # Add the selector and any required value displays
        ui_group["Config Selection"] = ModbusDatapoint(entity_data=EntityDataSelect(category=EntityCategory.CONFIG))
        ui_group.update({"Config Value Select": ModbusDatapoint(entity_data=EntityDataSelect(category=EntityCategory.CONFIG))} if has_select else {})
        ui_group.update({"Config Value Number": ModbusDatapoint(entity_data=EntityDataNumber(category=EntityCategory.CONFIG))} if has_number else {})

    def loadDatapoints(self):
        pass

    def loadTranslations(self, translations: dict):
        """Apply translations to select datapoint options."""
        if not translations:
            _LOGGER.debug("No translations provided for %s", self.model or type(self).__name__)
            return

        translated_count = 0

        for group, datapoints in self.Datapoints.items():
            for name, datapoint in datapoints.items():
                entity_data = datapoint.entity_data

                if not isinstance(entity_data, EntityDataSelect):
                    continue

                # Translations are keyed by datapoint name.
                option_translations = translations.get(name, {})

                if not isinstance(option_translations, dict) or not option_translations:
                    continue

                # Preserve option values; replace only display labels.
                entity_data.options = {
                    value: option_translations.get(label, label)
                    for value, label in entity_data.options.items()
                }

                translated_count += 1

        _LOGGER.debug("Applied translations to %d select datapoints for %s", translated_count, self.model or type(self).__name__)

    """ ******************************************************* """
    """ ************* FUNCTIONS CALLED ON EVENTS ************** """
    """ ******************************************************* """
    def onBeforeRead(self):
        pass
    def onAfterRead(self):
        pass
    def onAfterFirstRead(self):
        pass

    # Packet tracing
    def packet_trace(self, is_tx: bool, packet: bytes) -> bytes:
        _LOGGER.warning("DEVICE TRACE %s %d bytes", "TX" if is_tx else "RX", len(packet))
        if is_tx:
            self.traffic.record_tx(len(packet))
        else:
            self.traffic.record_rx(len(packet))
        return packet

    """ ******************************************************* """
    """ *********** EXTERNAL CALL TO READ ALL DATA ************ """
    """ ******************************************************* """
    async def readData(self):
        self.onBeforeRead()

        try:
            for group, _ in self.Datapoints.items():
                if group.poll_mode == ModbusPollMode.POLL_ON:
                    await self.readGroup(group)
                elif group.poll_mode == ModbusPollMode.POLL_ONCE and self.firstRead:
                    await self.readGroup(group)
        except Exception as err:
            raise

        if self.firstRead:   
            self.firstRead = False
            self.onAfterFirstRead()

        self.onAfterRead()

    """ ******************************************************* """
    """ ******************** READ GROUP *********************** """
    """ ******************************************************* """
    async def readGroup(self, group: ModbusGroup):
        """Read Modbus group registers and update data points."""
        MAX_REGISTERS_PER_READ = 125

        addresses = [
            (dp.address, dp.register_count)
            for dp in self.Datapoints[group].values()
        ]
        start_addr = min(addr for addr, _ in addresses)
        end_addr = max(addr + register_count for addr, register_count in addresses)
        n_reg = end_addr - start_addr

        if n_reg > MAX_REGISTERS_PER_READ:
            raise ValueError(
                f"Too many registers to read at once ({n_reg} requested, max {MAX_REGISTERS_PER_READ}) "
                f"for group {group}. Consider splitting the group."
        )

        method = self._get_read_method(group.mode)    
        response = await method(address=start_addr, count=n_reg, device_id=self._slave_id)

        # Handle Modbus errors
        if response.isError():
            raise ModbusException(f"Error reading group {group}: {response}")

        data = response.bits if group.mode in (ModbusMode.COILS, ModbusMode.DISCRETE_INPUTS) else response.registers
        _LOGGER.debug("Read data from address: %s - %s", start_addr, data)

        # Process the registers and update data points
        for name, dp in self.Datapoints[group].items():
            offset = dp.address - start_addr
            registers = data[offset:offset + dp.register_count]

            try:
                dp.from_modbus(registers, self.byte_order, self.word_order)
            except Exception as exc:
                _LOGGER.warning("Failed to decode datapoint %s in group %s (addr=%s len=%s raw=%s)", name, group, dp.address, dp.register_count, registers, exc_info=exc)
                raise

    """ ******************************************************* """
    """ **************** READ SINGLE VALUE ******************** """
    """ ******************************************************* """
    async def readValue(self, group: ModbusGroup, key: str) -> float | str:
        _LOGGER.debug("Reading value: Group: %s, Key: %s", group, key)

        if key not in self.Datapoints[group]:
            raise KeyError(f"Key '{key}' not found in group '{group}'")

        dp = self.Datapoints[group][key]
        register_count = dp.register_count

        method = self._get_read_method(group.mode) 
        response = await method(address=dp.address, count=register_count, device_id=self._slave_id)

        # Handle Modbus errors
        if response.isError():
            raise ModbusException(f"Error reading value for key '{key}': {response}")

        data = response.bits if group.mode in (ModbusMode.COILS, ModbusMode.DISCRETE_INPUTS) else response.registers
        _LOGGER.debug("Read data: %s", data)
        registers = data[:register_count]
        
        try:
            dp.from_modbus(registers, self.byte_order, self.word_order)
        except Exception as exc:
            _LOGGER.warning("Failed to decode datapoint %s in group %s (addr=%s len=%s raw=%s)", key, group, dp.address, dp.register_count, registers, exc_info=exc)
            raise

        return dp.value

    """ ******************************************************* """
    """ **************** WRITE SINGLE VALUE ******************* """
    """ ******************************************************* """
    async def writeValue(self, group: ModbusGroup, key: str, value: float):
        _LOGGER.debug("Writing value: Group: %s, Key: %s, Value: %s", group, key, value)

        if key not in self.Datapoints[group]:
            raise KeyError(f"Key '{key}' not found in group '{group}'")

        datapoint = self.Datapoints[group][key]
        register_count = datapoint.register_count
        if register_count > 2:
            raise ValueError(f"Unsupported register count: {register_count}. Only 1 or 2 registers are supported.")

        # Get value as modbus registers
        registers = datapoint.to_modbus(value, self.byte_order, self.word_order)

        # Write the registers
        address = datapoint.address

        if group.mode == ModbusMode.COILS:
            method = self._client.write_coil if register_count == 1 else self._client.write_coils
        elif group.mode == ModbusMode.HOLDING:
            method = self._client.write_register if register_count == 1 else self._client.write_registers
        else:
            raise ModbusException(f"Write Value: Unsupported Modbus mode {group.mode!r} for group {group!r}")

        if register_count == 1:
            response = await method(
                address=address,
                value=registers[0],
                device_id=self._slave_id,
            )
        else:
            response = await method(
                address=address,
                values=registers,
                device_id=self._slave_id,
            )

        if response.isError():
            raise ModbusException(f"Failed to write value for key '{key}': {response}")

        # Update the cached value
        datapoint.value = value
        _LOGGER.debug("Successfully wrote value for key '%s': %s", key, value)

    """ ******************************************************* """
    """ *********** HELPER FOR PROCESSING REGISTERS *********** """
    """ ******************************************************* """
    def _get_read_method(self, mode: ModbusMode):
        dispatch = {
            ModbusMode.INPUT:           self._client.read_input_registers,
            ModbusMode.DISCRETE_INPUTS: self._client.read_discrete_inputs,
            ModbusMode.HOLDING:         self._client.read_holding_registers,
            ModbusMode.COILS:           self._client.read_coils,
        }

        try:
            return dispatch[mode]
        except KeyError:
            raise ValueError(f"Unsupported Modbus mode: {mode}")