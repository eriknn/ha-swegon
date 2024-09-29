import logging

from collections import namedtuple
from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, CONF_IP
from .entity import SwegonBaseEntity

_LOGGER = logging.getLogger(__name__)

DATA_TYPE = namedtuple('DataType', ['deviceClass', 'category', 'icon'])
DATA_TYPES = {}
DATA_TYPES["Reset_Alarms"] = DATA_TYPE(None, None, "mdi:bell-cancel")

SwegonEntity = namedtuple('SwegonEntity', ['group', 'key', 'entityName', 'data_type'])
ENTITIES = [
    SwegonEntity("Config", "Reset_Alarms", "Reset Alarms", DATA_TYPES["Reset_Alarms"]),
]

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup button from a config entry created in the integrations UI."""
    # Create entities
    ha_entities = []

    # Find coordinator for this device
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create entities for this device
    for swegonentity in ENTITIES:
        ha_entities.append(SwegonButtonEntity(coordinator, swegonentity))

    async_add_devices(ha_entities, True)

class SwegonButtonEntity(SwegonBaseEntity, ButtonEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, swegonentity):
        super().__init__(coordinator, swegonentity)

        """Button Entity properties"""
        self._attr_device_class = swegonentity.data_type.deviceClass

    async def async_press(self) -> None:
        """ Write value to device """
        try:
            await self.coordinator.write_value(self._group, self._key, 1)
        except Exception as err:
            _LOGGER.debug("Error writing command: %s %s", self._group, self._key)         
        finally:
            self.async_schedule_update_ha_state(force_refresh=False)
