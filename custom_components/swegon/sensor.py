import logging

from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN
from .coordinator import ModbusCoordinator
from .entity import ModbusBaseEntity
from .entity_factory import create_entities

from .devices.datatypes import ModbusGroup, ModbusDatapoint, EntityDataSensor

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup entities from a config entry created in the integrations UI."""
    coordinator:ModbusCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(create_entities(coordinator, ModbusSensorEntity, EntityDataSensor))

class ModbusSensorEntity(ModbusBaseEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator:ModbusCoordinator, group:ModbusGroup, key:str, modbusDataPoint:ModbusDatapoint):
        """Initialize ModbusBaseEntity."""
        super().__init__(coordinator, group, key, modbusDataPoint)

    def _loadEntitySettings(self):
        """Sensor Entity properties"""
        self._attr_device_class = self.modbusDataPoint.entity_data.deviceClass
        self._attr_state_class = self.modbusDataPoint.entity_data.stateClass
        self._attr_native_unit_of_measurement = self.modbusDataPoint.entity_data.units
        self._attr_suggested_display_precision = self.modbusDataPoint.entity_data.precision

        """Cusom Entity properties"""
        self.enum = self.modbusDataPoint.entity_data.enum

    @property
    def native_value(self):
        """Return the value of the sensor."""
        val = self.coordinator.get_value(self._group, self._key)

        # Check if self.enum exists and is a dictionary
        if self.enum and isinstance(self.enum, dict):
            mapped_value = self.enum.get(val)
            if mapped_value is not None:
                return mapped_value
            else:
                return val
        else:
            # If no enum, return the raw value
            return val