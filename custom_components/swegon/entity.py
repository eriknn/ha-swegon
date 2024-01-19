"""Base entity class for Swegon integration."""
import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SwegonBaseEntity(CoordinatorEntity):
    """Swego base entity class."""

    def __init__(self, coordinator, swegonentity):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)

        """Generic Entity properties"""
        self._attr_entity_category = swegonentity.data_type.category
        self._attr_icon = swegonentity.data_type.icon
        self._attr_name = "{} {}".format(self.coordinator.devicename, swegonentity.entityName)
        self._attr_unique_id = "{}-{}".format(self.coordinator.device_id, self.name)
        self._attr_device_info = {
            "identifiers": self.coordinator.identifiers,
        }
        self._extra_state_attributes = {}
        
        """Store this entities key."""
        self._key = swegonentity.key

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._extra_state_attributes        
