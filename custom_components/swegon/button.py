import logging

from homeassistant.components.button import ButtonEntity

from .const import DOMAIN
from .coordinator import ModbusCoordinator
from .entity import ModbusBaseEntity
from .entity_factory import create_entities

from .devices.datatypes import ModbusGroup, ModbusDatapoint, EntityDataButton

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup entities from a config entry created in the integrations UI."""
    coordinator:ModbusCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(create_entities(coordinator, ModbusButtonEntity, EntityDataButton))

class ModbusButtonEntity(ModbusBaseEntity, ButtonEntity):
    """Representation of a Button."""

    def __init__(self, coordinator, group:ModbusGroup, key:str, modbusDataPoint:ModbusDatapoint):
        """Initialize ModbusBaseEntity."""
        super().__init__(coordinator, group, key, modbusDataPoint)

    def _loadEntitySettings(self):
        self._attr_device_class = self.modbusDataPoint.entity_data.deviceClass

    async def async_press(self) -> None:
        """ Write value to device """
        try:
            await self.coordinator.write_value(self._group, self._key, 1)
        except Exception as err:
            _LOGGER.debug("Error writing command: %s %s", self._group, self._key)         
        finally:
            self.async_schedule_update_ha_state(force_refresh=False)
