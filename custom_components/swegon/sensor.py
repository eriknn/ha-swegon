import logging

from collections import namedtuple
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import CONF_DEVICES, PERCENTAGE, TEMPERATURE, CONCENTRATION_PARTS_PER_MILLION
from homeassistant.const import UnitOfPressure, UnitOfTemperature, UnitOfVolumeFlowRate
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers.entity import EntityCategory

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

SwegonEntity = namedtuple('SwegonEntity', ['group', 'key', 'entityName', 'data_type'])
ENTITIES = [
    SwegonEntity("Sensors", "Fresh_Temp", "Fresh Air Temp", DATA_TYPES["temperature"]),
    SwegonEntity("Sensors", "Supply_Temp1", "Supply Temp before re-heater", DATA_TYPES["temperature"]),
    SwegonEntity("Sensors", "Supply_Temp2", "Supply Temp", DATA_TYPES["temperature"]),
    SwegonEntity("Sensors", "Extract_Temp", "Extract Temp", DATA_TYPES["temperature"]),
    SwegonEntity("Sensors", "Exhaust_Temp", "Exhaust Temp", DATA_TYPES["temperature"]),
    #SwegonEntity("Sensors", "Room_Temp", "Room Air Temp", DATA_TYPES["temperature"]),
    SwegonEntity("Sensors", "UP1_Temp", "User Panel 1 Temp", DATA_TYPES["temperature"]),
    #SwegonEntity("Sensors", "UP2_Temp", "User Panel 2 Temp", DATA_TYPES["temperature"]),
    #SwegonEntity("Sensors", "WR_Temp", "Water Radiator Temp", DATA_TYPES["temperature"]),
    #SwegonEntity("Sensors", "PreHeat_Temp", "Pre-Heater Temp", DATA_TYPES["temperature"]),
    #SwegonEntity("Sensors", "ExtFresh_Temp", "External Fresh Air Temp", DATA_TYPES["temperature"]),
    #SwegonEntity("Sensors", "C02_Unf", "CO2 Unfiltered", DATA_TYPES["co2"]),
    #SwegonEntity("Sensors", "CO2_Fil", "CO2 Filtered", DATA_TYPES["co2"]),
    SwegonEntity("Sensors", "RH", "Relative Humidity", DATA_TYPES["humidity"]),
    SwegonEntity("Sensors", "AH", "Absolute Humidity", DATA_TYPES["humidity_abs"]),
    #SwegonEntity("Sensors", "AH_SP", "Absolute Humidity SP", DATA_TYPES["humidity_abs"]),
    #SwegonEntity("Sensors", "VOC", "VOC", DATA_TYPES["voc"]),
    #SwegonEntity("Sensors", "Supply_Pressure", "Supply Pressure", DATA_TYPES["pressure"]),
    #SwegonEntity("Sensors", "Exhaust_Pressure", "Exhaust Pressure", DATA_TYPES["pressure"]),
    #SwegonEntity("Sensors", "Supply_Flow", "Supply Flow", DATA_TYPES["flow"]),
    #SwegonEntity("Sensors", "Exhaust_Flow", "Exhaust Flow", DATA_TYPES["flow"]),
    SwegonEntity("Sensors2", "Heat_Exchanger", "Heat Exchanger", DATA_TYPES["percent"]),
    SwegonEntity("UnitStatuses", "Supply_Fan", "Supply Fan", DATA_TYPES["percent"]),
    SwegonEntity("UnitStatuses", "Exhaust_Fan", "Exhaust Fan", DATA_TYPES["percent"]),
    SwegonEntity("UnitStatuses", "Heating_Output", "Heating Output", DATA_TYPES["percent"]),
    SwegonEntity("VirtualSensors", "Efficiency", "Efficiency", DATA_TYPES["percent"]),
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
        val = self.coordinator.get_value(self._group, self._key)
        return val
