import logging

from collections import namedtuple
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_DEVICES
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, CONF_IP
from .entity import SwegonBaseEntity

_LOGGER = logging.getLogger(__name__)
DATA_TYPE = namedtuple('DataType', ['category', 'icon'])

SwegonEntity = namedtuple('SwegonEntity', ['group', 'key', 'entityName', 'data_type'])
ENTITIES = [
    SwegonEntity("Commands", "Fireplace_Mode", "Fireplace Mode", DATA_TYPE(None, None)),
    SwegonEntity("Commands", "Travelling_Mode", "Travelling Mode", DATA_TYPE(None, None)),
]

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup switch from a config entry created in the integrations UI."""
    # Create entities
    ha_entities = []

    # Find coordinator for this device
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create entities for this device
    for swegonentity in ENTITIES:
        ha_entities.append(SwegonSwitchEntity(coordinator, swegonentity))

    async_add_devices(ha_entities, True)


class SwegonSwitchEntity(SwegonBaseEntity, SwitchEntity):
    """Representation of a Switch."""

    def __init__(self, coordinator, swegonentity):
        """Pass coordinator to SwegonEntity."""
        super().__init__(coordinator, swegonentity)

    @property
    def is_on(self):
        """Return the state of the switch."""
        return self.coordinator.get_value(self._group, self._key)

    async def async_turn_on(self, **kwargs):
        await self.writeValue(1)

    async def async_turn_off(self, **kwargs):
        await self.writeValue(0)

    async def writeValue(self, value):
        """ Write value to device """
        try:
            await self.coordinator.write_value(self._group, self._key, value)
        except Exception as err:
            _LOGGER.debug("Error writing command: %s %s", self._group, self._key)
        finally:
            self.async_schedule_update_ha_state(force_refresh=False)
