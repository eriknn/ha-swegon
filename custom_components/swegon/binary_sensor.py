import logging

from collections import namedtuple
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, CONF_IP
from .entity import SwegonBaseEntity

_LOGGER = logging.getLogger(__name__)

DATA_TYPE = namedtuple('DataType', ['deviceClass', 'category', 'icon'])
DATA_TYPES = {}
DATA_TYPES["Active_Alarms"] = DATA_TYPE(BinarySensorDeviceClass.PROBLEM, None, "mdi:bell")

SwegonEntity = namedtuple('SwegonEntity', ['group', 'key', 'entityName', 'data_type'])
ENTITIES = [
    SwegonEntity("Alarms", "Active_Alarms", "Active Alarms", DATA_TYPES["Active_Alarms"]),
]

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor from a config entry created in the integrations UI."""
    # Create entities
    ha_entities = []

    # Find coordinator for this device
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create entities for this device
    for swegonentity in ENTITIES:
        ha_entities.append(SwegonBinarySensorEntity(coordinator, swegonentity))

    async_add_devices(ha_entities, True)


class SwegonBinarySensorEntity(SwegonBaseEntity, BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, swegonentity):
        super().__init__(coordinator, swegonentity)

        """Sensor Entity properties"""
        self._attr_device_class = swegonentity.data_type.deviceClass

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        attrs = {}
        alarms = self.coordinator._swegonDevice.Datapoints["Alarms"]
        for (dataPointName, data) in alarms.items():
            if data.Value:
                newAttr = {dataPointName:"ALARM"}
                attrs.update(newAttr)
        return attrs
        
    @property
    def is_on(self):
        """Return the state of the switch."""
        return self.coordinator.get_value(self._group, self._key)
