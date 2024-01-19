import logging

from collections import namedtuple
from homeassistant.components.select import SelectEntity
from homeassistant.const import CONF_DEVICES
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, CONF_IP
from .entity import SwegonBaseEntity

_LOGGER = logging.getLogger(__name__)

# Creating nested dictionary of key/pairs
OPTIONS = {
    "Op_Mode": {0: "Stopped", 1: "Away", 2: "Home", 3: "Boost", 4: "Travelling"},
}

DATA_TYPE = namedtuple('DataType', ['category', 'icon'])

SwegonEntity = namedtuple('SwegonEntity', ['key', 'entityName', 'data_type', 'options'])
ENTITIES = [
    SwegonEntity("Op_Mode", "Operating Mode", DATA_TYPE(None, None), OPTIONS["Op_Mode"])
]

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup selects from a config entry created in the integrations UI."""
    # Create entities
    ha_entities = []

    # Find coordinator for this device
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create entities for this device
    for swegonentity in ENTITIES:
        ha_entities.append(SwegonSelectEntity(coordinator, swegonentity))

    async_add_devices(ha_entities, True)


class SwegonSelectEntity(SwegonBaseEntity, SelectEntity):
    """Representation of a Select."""

    def __init__(self, coordinator, swegonentity):
        """Pass coordinator to SwegonEntity."""
        super().__init__(coordinator, swegonentity)

        """Select Entity properties"""
        self._options = swegonentity.options

    @property
    def current_option(self):
        try:
            optionIndex = self.coordinator.get_value(self._key)
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
        await self.coordinator.write_value(self._key, value)
        self.async_schedule_update_ha_state(force_refresh=False)
