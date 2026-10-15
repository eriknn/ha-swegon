import logging

from homeassistant.components.number import NumberEntity

from .const import DOMAIN
from .coordinator import ModbusCoordinator
from .entity import ModbusBaseEntity
from .entity_factory import create_entities

from .devices.datatypes import ModbusGroup, ModbusDefaultGroups, ModbusNumber

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup entities from a config entry created in the integrations UI."""
    coordinator:ModbusCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(create_entities(coordinator, ModbusNumberEntity, ModbusNumber))

class ModbusNumberEntity(ModbusBaseEntity, NumberEntity):
    """Representation of a Number."""

    def __init__(self, coordinator:ModbusCoordinator, group:ModbusGroup, key:str, modbusDataPoint:ModbusNumber):
        """Initialize ModbusBaseEntity."""
        super().__init__(coordinator, group, key, modbusDataPoint)

        """ Give coordinator handle to config value entity """
        if group == ModbusDefaultGroups.UI and key == "Config Value Number":
            coordinator.config_value_number = self 
            self._attr_device_info = None       # Hide entity

    def _loadEntitySettings(self):
        self._attr_device_class = self.modbusDataPoint.deviceClass
        self._attr_mode = "box"
        self._attr_native_min_value = self.modbusDataPoint.min_value
        self._attr_native_max_value = self.modbusDataPoint.max_value
        self._attr_native_step = self.modbusDataPoint.step
        self._attr_native_unit_of_measurement = self.modbusDataPoint.units

    @property
    def native_value(self) -> float | None:
        """Return number value."""
        val = self.coordinator.get_value(self._group, self._key)
        return val

    async def async_set_native_value(self, value):
        """ Write value to device """
        try:
            await self.coordinator.write_value(self._group, self._key, value)
        except Exception as err:
            _LOGGER.debug("Error writing command: %s %s", self._group, self._key)
        finally:
            self.async_schedule_update_ha_state(force_refresh=False)
            
