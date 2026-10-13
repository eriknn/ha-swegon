import logging

from homeassistant.components.select import SelectEntity

from .const import DOMAIN
from .coordinator import ModbusCoordinator
from .entity import ModbusBaseEntity
from .entity_factory import create_entities

from .devices.datatypes import ModbusGroup, ModbusDefaultGroups, ModbusDatapoint, EntityDataSelect

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup entities from a config entry created in the integrations UI."""
    coordinator:ModbusCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(create_entities(coordinator, ModbusSelectEntity, EntityDataSelect))

class ModbusSelectEntity(ModbusBaseEntity, SelectEntity):
    """Representation of a Select."""

    def __init__(self, coordinator:ModbusCoordinator, group:ModbusGroup, key:str, modbusDataPoint:ModbusDatapoint):
        """Initialize ModbusBaseEntity."""
        super().__init__(coordinator, group, key, modbusDataPoint)

        """ Give coordinator handle to config value entity """
        if group == ModbusDefaultGroups.UI and key == "Config Value Select":
            coordinator.config_value_select = self
            self._attr_device_info = None       # Hide entity

    def _loadEntitySettings(self):
        if self._key == "Config Selection":
            self._options = self.coordinator.get_config_options()
        else:
            self._options = self.modbusDataPoint.entity_data.options

    @property
    def current_option(self):
        try:
            if self._key == "Config Selection":
                optionIndex = self.config_selection
                option = self._options[optionIndex]
            else:
                optionIndex = self.coordinator.get_value(self._group, self._key)
                option = self._options[optionIndex]
        except Exception as e:
            option = "Unknown"
        return option

    @property
    def options(self):
        return list(self._options.values())

    async def async_select_option(self, option):
        """ Find new value """
        value = None

        for key, val in self._options.items():
            if val == option:
                value = key
                break

        if value is None:
            return

        """ Write value to device """
        _LOGGER.debug("Select: %s", self._key)
        try:
            if self._key == "Config Selection":
                self.config_selection = value
                await self.coordinator.config_select(option)
            else:           
                _LOGGER.debug("Writing")
                await self.coordinator.write_value(self._group, self._key, value)
        except Exception as err:
            _LOGGER.debug("Error writing command: %s %s", self._group, self._key, exc_info=True)
        finally:
            self.async_schedule_update_ha_state(force_refresh=False)
