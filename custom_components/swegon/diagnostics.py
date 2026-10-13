import logging

from .const import DOMAIN
from .coordinator import ModbusCoordinator

from .devices.modbusdevice import ModbusDevice
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry
from typing import Any

async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    return await _getStats(hass, entry)

async def async_get_device_diagnostics(hass: HomeAssistant, entry: ConfigEntry, device: DeviceEntry) -> dict[str, Any]:
    return await _getStats(hass, entry)

async def _getStats(hass: HomeAssistant, entry: ConfigEntry)  -> dict[str, Any]:
    # Get coordinator for this config entry
    coordinator: ModbusCoordinator = hass.data[DOMAIN][entry.entry_id]

    # The ModbusDevice is stored inside the coordinator
    modbus_device: ModbusDevice = coordinator._modbusDevice

    dev_traffic = modbus_device.traffic                 # Device traffic
    bus_traffic = modbus_device._client._bus.traffic    # Total traffic on endpoint

    return {
        "manufacturer": modbus_device.manufacturer,
        "model": modbus_device.model,
        "slave_id": modbus_device._slave_id,

        "device": dev_traffic.to_dict(),
        "endpoint": bus_traffic.to_dict(),
    }