import logging

from collections import namedtuple
from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.const import CONF_DEVICES
from homeassistant.const import UnitOfTemperature
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, CONF_IP
from .entity import SwegonBaseEntity

_LOGGER = logging.getLogger(__name__)

LimitsTuple = namedtuple('limits', ['min_value', 'max_value', 'step'])
LIMITS = {}
LIMITS["temperature"] = LimitsTuple(13, 25, 0.1)
LIMITS["config"] = LimitsTuple(-2147483648, 2147483647, 1)

DATA_TYPE = namedtuple('DataType', ['units', 'deviceClass', 'category', 'icon'])
DATA_TYPES = {}
DATA_TYPES["temperature"] = DATA_TYPE(UnitOfTemperature.CELSIUS, NumberDeviceClass.TEMPERATURE, None, None)
DATA_TYPES["config"] = DATA_TYPE(None, None, EntityCategory.CONFIG, None)

SwegonEntity = namedtuple('SwegonEntity', ['group', 'key', 'entityName', 'data_type', 'limits'])
ENTITIES = [
    SwegonEntity("Setpoints", "Temp_SP", "Temperature Setpoint", DATA_TYPES["temperature"], LIMITS["temperature"]),
    SwegonEntity("Config", "Config_Value", "Config Value", DATA_TYPES["config"], LIMITS["config"]),
]

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup number from a config entry created in the integrations UI."""
    # Create entities
    ha_entities = []

    # Find coordinator for this device
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create entities for this device
    for swegonentity in ENTITIES:
        ha_entities.append(SwegonNumberEntity(coordinator, swegonentity))

    async_add_devices(ha_entities, True)

class SwegonNumberEntity(SwegonBaseEntity, NumberEntity):
    """Representation of a Number."""

    def __init__(self, coordinator, swegonentity):
        """Pass coordinator to PaxCalimaEntity."""
        super().__init__(coordinator, swegonentity)

        """Number Entity properties"""
        self._attr_device_class = swegonentity.data_type.deviceClass
        self._attr_mode = "box"
        self._attr_native_min_value = swegonentity.limits.min_value
        self._attr_native_max_value = swegonentity.limits.max_value
        self._attr_native_step = swegonentity.limits.step
        self._attr_native_unit_of_measurement = swegonentity.data_type.units

        """Callback for updated value"""
        coordinator.registerOnUpdateCallback(self._key, self.update_callback)

    async def update_callback(self, newKey):
        self._key = newKey
        self.async_schedule_update_ha_state(force_refresh=False)

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
            
