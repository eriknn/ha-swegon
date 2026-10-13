import logging

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DOMAIN
from .coordinator import ModbusCoordinator
from .entity import ModbusBaseEntity
from .entity_factory import create_entities

from .devices.datatypes import ModbusGroup, ModbusDatapoint, EntityDataBinarySensor

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup entities from a config entry created in the integrations UI."""
    coordinator:ModbusCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(create_entities(coordinator, ModbusBinarySensorEntity, EntityDataBinarySensor))

class ModbusBinarySensorEntity(ModbusBaseEntity, BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, group:ModbusGroup, key:str, modbusDataPoint:ModbusDatapoint):
        """Initialize ModbusBaseEntity."""
        super().__init__(coordinator, group, key, modbusDataPoint)

    def _loadEntitySettings(self):
        self._attr_device_class = self.modbusDataPoint.entity_data.deviceClass

    @property
    def is_on(self):
        """Return the state of the switch."""
        value = self.coordinator.get_value(self._group, self._key)
        return value is not None and value >= 1
