import async_timeout
import datetime as dt
import logging

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed, ConfigEntryNotReady, ConfigEntryError

from .busmanager import BusClient
from .devices.datatypes import ModbusDefaultGroups, ModbusDatapoint
from .devices.datatypes import ModbusSelect, ModbusNumber
from .devices.modbusdevice import ModbusDevice
from .entity import ModbusBaseEntity

# Import device models
from .const import DEVICE_CASA_R4, DEVICE_CASA_R7, DEVICE_CASA_R15
from .devices.Swegon.CASA_R4 import Device as CASA_R4
from .devices.Swegon.CASA_R7 import Device as CASA_R7
from .devices.Swegon.CASA_R15 import Device as CASA_R15

# For translations
from homeassistant.util.json import load_json
from importlib import import_module
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

DEVICE_CLASSES = {
    DEVICE_CASA_R4: CASA_R4,
    DEVICE_CASA_R7: CASA_R7,
    DEVICE_CASA_R15: CASA_R15,
}

class ModbusCoordinator(DataUpdateCoordinator):    
    def __init__(self, hass, device_entry, device_model:str, scan_interval, scan_interval_fast, bus:BusClient):
        """Initialize coordinator parent"""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="ModbusDevice: " + device_entry.name,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=dt.timedelta(seconds=scan_interval),
        )

        self.device_model = device_model
        self.bus = bus

        self._fast_poll_enabled = False
        self._fast_poll_count = 0
        self._normal_poll_interval = scan_interval
        self._fast_poll_interval = scan_interval_fast

        self._device_entry = device_entry

        self._modbusDevice: ModbusDevice | None = None

        # Storage for config selection
        self.config_value_select:ModbusBaseEntity = None
        self.config_value_number:ModbusBaseEntity = None
        self.config_value_active:ModbusBaseEntity = None

    async def _async_setup(self):
        # Find device class and instantiate it
        device_class = DEVICE_CLASSES.get(self.device_model)

        if device_class is None:
            raise ConfigEntryError(f"Unsupported device model: {self.device_model}")

        try:
            self._modbusDevice = device_class(self.bus)
            await self._load_translations(device_class)
        except Exception as err:
            raise ConfigEntryNotReady("Could not read data from device!") from err

    async def _load_translations(self, device_class):
        # Load translations for device
        try:
            # Locate the device-specific translation file.
            module = import_module(device_class.__module__)
            device_file = Path(module.__file__)
            translation_dir = device_file.parent / "translations"

            language = self.hass.config.language.split("-")[0].split("_")[0]
            translation_file = translation_dir / f"{language}.json"

            if not translation_file.is_file():
                _LOGGER.debug("Device %s has no translations for language '%s'; using defaults", self.name, language)
                return

            translations = await self.hass.async_add_executor_job(load_json, translation_file)

            self._modbusDevice.loadTranslations(translations)

        except Exception as err:
            raise ConfigEntryNotReady(
                "Could not initialize device or load translations!"
            ) from err

    def close(self):
        """Close the underlying device safely."""
        self._modbusDevice.close()

    @property
    def device_id(self):
        return self._device_entry.id

    @property
    def devicename(self):
        return self._device_entry.name

    @property
    def identifiers(self):
        return self._device_entry.identifiers

    def setFastPollMode(self):
        _LOGGER.debug("Enabling fast poll mode")
        self._fast_poll_enabled = True
        self._fast_poll_count = 0
        self.update_interval = dt.timedelta(seconds=self._fast_poll_interval)
        self._schedule_refresh()

    def setNormalPollMode(self):
        _LOGGER.debug("Enabling normal poll mode")
        self._fast_poll_enabled = False
        self.update_interval = dt.timedelta(seconds=self._normal_poll_interval)


    async def _async_update_data(self):
        _LOGGER.debug("Coordinator updating data for: %s", self.devicename) 

        """ Counter for fast polling """
        if self._fast_poll_enabled:
            self._fast_poll_count += 1
            if self._fast_poll_count > 5:
                self.setNormalPollMode()

        """ Fetch data """
        try:
            async with async_timeout.timeout(20):
                # Read main configured data
                await self._modbusDevice.readData()  

                # Also read our config selection
                if self.config_value_active is not None:
                    await self._modbusDevice.readValue(ModbusDefaultGroups.CONFIG, self.config_value_active._key)
        except Exception as err:
            _LOGGER.warning("Failed to update %s: %s", self.devicename, err)
            raise UpdateFailed from err
        
        await self._async_update_deviceInfo()

    async def _async_update_deviceInfo(self) -> None:
        device_registry = dr.async_get(self.hass)
        device_registry.async_update_device(
            self.device_id,
            manufacturer=self._modbusDevice.manufacturer,
            model=self._modbusDevice.model,
            sw_version=self._modbusDevice.sw_version,
            serial_number=self._modbusDevice.serial_number,
        )
        _LOGGER.debug("Updated device data for: %s", self.devicename) 

    ################################
    ######## Configuration #########
    ################################   
    async def _swap_config_value_entity(self, datapoint: ModbusDatapoint):
        _LOGGER.debug("Changing CONFIG value entity type")

        # Disable old entity
        if self.config_value_active is not None:
            self.config_value_active.toggle_entity_visibility(self.hass, False)
            self.config_value_active = None

        # Select active entity
        if isinstance(datapoint, ModbusNumber):
            self.config_value_active = self.config_value_number
        elif isinstance(datapoint, ModbusSelect):
            self.config_value_active = self.config_value_select
        else:
            _LOGGER.warning("Entity type not supported for config!")
            return

        # Enable active entity
        self.config_value_active.toggle_entity_visibility(self.hass, True)

    async def config_select(self, key):
        _LOGGER.debug("In config select: %s", key)

        # Change type of entitiy for config value
        old_dp = self.config_value_active.modbusDataPoint if self.config_value_active else None
        new_dp = self._modbusDevice.Datapoints[ModbusDefaultGroups.CONFIG][key]

        _LOGGER.debug("Dps: %s %s", old_dp, new_dp)

        if old_dp is None or type(old_dp) != type(new_dp):
            _LOGGER.debug("New type!")
            await self._swap_config_value_entity(new_dp)
        try:
            # Update entity settings and read value
            self.config_value_active.modbusDataPoint = new_dp
            self.config_value_active._group = ModbusDefaultGroups.CONFIG
            self.config_value_active._key = key
            self.config_value_active.rename(self.hass, key)
            self.config_value_active._loadEntitySettings()
            await self._modbusDevice.readValue(ModbusDefaultGroups.CONFIG, key)
        finally:
            self.config_value_active.async_write_ha_state()

    def get_config_options(self):
        options = {}
        for i, config in enumerate(self._modbusDevice.Datapoints[ModbusDefaultGroups.CONFIG]):
            options.update({i:config})
        return options

    ################################
    ######### Read / Write #########
    ################################   
    def get_value(self, group, key):
        if group in self._modbusDevice.Datapoints:
            if key in self._modbusDevice.Datapoints[group]:
                return self._modbusDevice.Datapoints[group][key].value
        return None

    def get_attrs(self, group, key):
        if group in self._modbusDevice.Datapoints:
            if key in self._modbusDevice.Datapoints[group]:
                return self._modbusDevice.Datapoints[group][key].attrs
        return None

    async def write_value(self, group, key, value):
        _LOGGER.debug("Write_Data: %s - %s - %s", group, key, value)
        try:
            await self._modbusDevice.writeValue(group, key, value)
        except Exception as exc:
            _LOGGER.error("Failed to write value '%s' to key '%s' in group '%s': %s", value, key, group, exc, exc_info=exc)
            raise

        self.setFastPollMode()