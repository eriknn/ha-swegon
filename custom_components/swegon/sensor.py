import logging

from collections import namedtuple
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import CONF_DEVICES, PERCENTAGE, TEMPERATURE, CONCENTRATION_PARTS_PER_MILLION
from homeassistant.const import UnitOfPressure, UnitOfTemperature, UnitOfVolumeFlowRate
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, CONF_IP
from .entity import SwegonBaseEntity

_LOGGER = logging.getLogger(__name__)

DATA_TYPE = namedtuple('DataType', ['units', 'deviceClass', 'category', 'icon'])
DATA_TYPES = {}
DATA_TYPES["co2"] = DATA_TYPE(CONCENTRATION_PARTS_PER_MILLION, SensorDeviceClass.CO2, None, None)
DATA_TYPES["flow"] = DATA_TYPE(UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR, None, None, "mdi:weather-windy")
DATA_TYPES["humidity"] = DATA_TYPE(PERCENTAGE, SensorDeviceClass.HUMIDITY, None, None)
DATA_TYPES["humidity_abs"] = DATA_TYPE("g/m³", None, None, None)
DATA_TYPES["percent"] = DATA_TYPE(PERCENTAGE, None, None, None)
DATA_TYPES["pressure"] = DATA_TYPE(UnitOfPressure.PA, SensorDeviceClass.PRESSURE, None, None)
DATA_TYPES["temperature"] = DATA_TYPE(UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None, None)
DATA_TYPES["voc"] = DATA_TYPE(CONCENTRATION_PARTS_PER_MILLION, SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS, None, None)

SwegonEntity = namedtuple('SwegonEntity', ['key', 'entityName', 'data_type'])
ENTITIES = [
    SwegonEntity("Fresh_T", "Fresh Air Temp", DATA_TYPES["temperature"]),
    SwegonEntity("Supply_T1", "Supply Temp before re-heater", DATA_TYPES["temperature"]),
    SwegonEntity("Supply_T2", "Supply Temp", DATA_TYPES["temperature"]),
    SwegonEntity("Extract_T", "Extract Temp", DATA_TYPES["temperature"]),
    SwegonEntity("Exhaust_T", "Exhaust Temp", DATA_TYPES["temperature"]),
    SwegonEntity("Room_T", "Room Air Temp", DATA_TYPES["temperature"]),
    SwegonEntity("UP1_T", "User Panel 1 Temp", DATA_TYPES["temperature"]),
    SwegonEntity("UP2_T", "User Panel 2 Temp", DATA_TYPES["temperature"]),
    SwegonEntity("WR_T", "Water Radiator Temp", DATA_TYPES["temperature"]),
    SwegonEntity("PreHeat_T", "Pre-Heater Temp", DATA_TYPES["temperature"]),
    SwegonEntity("ExtFresh_T", "External Fresh Air Temp", DATA_TYPES["temperature"]),
    SwegonEntity("C02_Unf", "CO2 Unfiltered", DATA_TYPES["co2"]),
    SwegonEntity("CO2_Fil", "CO2 Filtered", DATA_TYPES["co2"]),
    SwegonEntity("RH", "Relative Humidity", DATA_TYPES["humidity"]),
    SwegonEntity("AH", "Absolute Humidity", DATA_TYPES["humidity_abs"]),
    SwegonEntity("AH_SP", "Absolute Humidity SP", DATA_TYPES["humidity_abs"]),
    SwegonEntity("VOC", "VOC", DATA_TYPES["voc"]),
    SwegonEntity("Supp_P", "Supply Pressure", DATA_TYPES["pressure"]),
    SwegonEntity("Ex_P", "Exhaust Pressure", DATA_TYPES["pressure"]),
    SwegonEntity("Supp_Flow", "Supply Flow", DATA_TYPES["flow"]),
    SwegonEntity("Ex_Flow", "Exhaust Flow", DATA_TYPES["flow"]),
    SwegonEntity("Supply_Fan", "Supply Fan", DATA_TYPES["percent"]),
    SwegonEntity("Exhaust_Fan", "Exhaust Fan", DATA_TYPES["percent"]),
    SwegonEntity("Heating_Output", "Heating Output", DATA_TYPES["percent"]),
]

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor from a config entry created in the integrations UI."""
    # Create entities
    ha_entities = []

    # Find coordinator for this device
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create entities for this device
    for swegonentity in ENTITIES:
        ha_entities.append(SwegonSensorEntity(coordinator, swegonentity))

    async_add_devices(ha_entities, True)


class SwegonSensorEntity(SwegonBaseEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, swegonentity):
        super().__init__(coordinator, swegonentity)

        """Sensor Entity properties"""
        self._attr_device_class = swegonentity.data_type.deviceClass
        self._attr_native_unit_of_measurement = swegonentity.data_type.units

    @property
    def native_value(self):
        """Return the value of the sensor."""
        val = self.coordinator.get_value(self._key)
        return val
