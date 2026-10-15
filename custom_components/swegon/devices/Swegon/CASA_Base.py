####################################################
##### Based on Swegon CASA Genius Register 4.2 #####
####################################################

import logging

from ..modbusdevice import ModbusDevice
from ..const import ModbusMode, ModbusPollMode, ModbusDataType
from ..datatypes import ModbusDatapoint, ModbusGroup, ModbusDefaultGroups
from ..datatypes import ModbusSensor, ModbusSelect, ModbusNumber, ModbusBinarySensor, ModbusSwitch, ModbusButton

from homeassistant.const import UnitOfTemperature, UnitOfTime, UnitOfRatio
from homeassistant.const import PERCENTAGE
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.number import NumberDeviceClass

_LOGGER = logging.getLogger(__name__)

# Define groups
GROUP_COMMANDS = ModbusGroup(ModbusMode.HOLDING, ModbusPollMode.POLL_ON)
GROUP_COMMANDS2 = ModbusGroup(ModbusMode.HOLDING, ModbusPollMode.POLL_OFF) 
GROUP_SETPOINTS = ModbusGroup(ModbusMode.HOLDING, ModbusPollMode.POLL_ON)
GROUP_DEVICE_INFO = ModbusGroup(ModbusMode.INPUT, ModbusPollMode.POLL_ONCE)
GROUP_ALARMS = ModbusGroup(ModbusMode.INPUT, ModbusPollMode.POLL_ON)
GROUP_SENSORS = ModbusGroup(ModbusMode.INPUT, ModbusPollMode.POLL_ON)
GROUP_UNIT_STATUSES = ModbusGroup(ModbusMode.INPUT, ModbusPollMode.POLL_ON)  
GROUP_UI = ModbusGroup(ModbusMode.NONE, ModbusPollMode.POLL_OFF) 

class Device(ModbusDevice):
    # Override static device information
    manufacturer = "Swegon"
    model = "CASA"

    def loadDatapoints(self):
        # COMMANDS - Read/Write
        self.Datapoints[GROUP_COMMANDS] = {
            "Operating Mode": ModbusSelect(address=5000, options={0: "Stopped", 1: "Away", 2: "Home", 3: "Boost", 4: "Travel"}),
            "Fireplace Mode": ModbusSwitch(address=5001),
            "Travelling Mode": ModbusSwitch(address=5003),
        }

        # COMMANDS2 - Write
        self.Datapoints[GROUP_COMMANDS2] = {
            "Reset Alarms": ModbusButton(address=5405),
        }

        # SETPOINTS - Read/Write
        self.Datapoints[GROUP_SETPOINTS] = {
            "Temperature Setpoint": ModbusNumber(address=5100, scaling=0.1, deviceClass=NumberDeviceClass.TEMPERATURE, units=UnitOfTemperature.CELSIUS, min_value=13, max_value=25, step=0.1)
        }

        # DEVICE_INFO - Read-only
        self.Datapoints[GROUP_DEVICE_INFO] = {
            "FW Maj": ModbusDatapoint(address=6000),
            "FW Min": ModbusDatapoint(address=6001),
            "FW Build": ModbusDatapoint(address=6002),
            "Par Maj": ModbusDatapoint(address=6003),
            "Par Min": ModbusDatapoint(address=6004),
            "Model Name": ModbusDatapoint(address=6007, register_count=15, type=ModbusDataType.STRING1),        # 15 registers, 1 char per reg
            "Serial Number": ModbusDatapoint(address=6023, register_count=24, type=ModbusDataType.STRING1),     # 24 registers, 1 char per reg
        }

        # ALARMS - Read-only
        self.Datapoints[GROUP_ALARMS] = {
            "T1 Failure": ModbusDatapoint(address=6100),
            "T2 Failure": ModbusDatapoint(address=6101),
            "T3 Failure": ModbusDatapoint(address=6102),
            "T4 Failure": ModbusDatapoint(address=6103),
            "T5 Failure": ModbusDatapoint(address=6104),
            "T6 Failure": ModbusDatapoint(address=6105),
            "T7 Failure": ModbusDatapoint(address=6106),
            "T8 Failure": ModbusDatapoint(address=6107),
            "T1 Failure Unconf": ModbusDatapoint(address=6108),
            "T2 Failure Unconf": ModbusDatapoint(address=6109),
            "T3 Failure Unconf": ModbusDatapoint(address=6110),
            "T4 Failure Unconf": ModbusDatapoint(address=6111),
            "T5 Failure Unconf": ModbusDatapoint(address=6112),
            "T6 Failure Unconf": ModbusDatapoint(address=6113),
            "T7 Failure Unconf": ModbusDatapoint(address=6114),
            "T8 Failure Unconf": ModbusDatapoint(address=6115),
            "Afterheater Failure": ModbusDatapoint(address=6116),
            "Afterheater Failure Unconf": ModbusDatapoint(address=6117),
            "Preheater Failure": ModbusDatapoint(address=6118),
            "Preheater Failure Unconf": ModbusDatapoint(address=6119),
            "Freezing Danger": ModbusDatapoint(address=6120),
            "Freezing Danger Unconf": ModbusDatapoint(address=6121),
            "New Genius Alarm": ModbusDatapoint(address=6122),
            "New Genius Alarm Unconf": ModbusDatapoint(address=6123),
            "Supply Fan Failure": ModbusDatapoint(address=6124),
            "Supply Fan Failure Unconf": ModbusDatapoint(address=6125),
            "Exhaust Fan Failure": ModbusDatapoint(address=6126),
            "Exhaust Fan Failure Unconf": ModbusDatapoint(address=6127),
            "Service Info": ModbusDatapoint(address=6128),
            "Filter Guard Info": ModbusDatapoint(address=6129),
            "Emergency Stop": ModbusDatapoint(address=6130),
            "Active Alarms": ModbusBinarySensor(address=6131, deviceClass=BinarySensorDeviceClass.PROBLEM, icon="mdi:bell"),
            "Info Unconf": ModbusDatapoint(address=6132),
            "Preheater temperature high": ModbusDatapoint(address=6140),
            "Preheater temperature high Unconf": ModbusDatapoint(address=6141),
            "Supply temperature low": ModbusDatapoint(address=6142),
            "Supply temperature low Unconf": ModbusDatapoint(address=6143),
            "Supply temperature high": ModbusDatapoint(address=6144),
            "Supply temperature high Unconf": ModbusDatapoint(address=6144),
            "Rotor": ModbusDatapoint(address=6146),
            "Rotor Unconf": ModbusDatapoint(address=6147),
            "Fan control": ModbusDatapoint(address=6148),
            "Fan control Unconf": ModbusDatapoint(address=6149),
        }

        # SENSORS - Read
        self.Datapoints[GROUP_SENSORS] = {
            "Fresh Air Temp": ModbusSensor(address=6200, scaling=0.1, deviceClass=SensorDeviceClass.TEMPERATURE, stateClass=SensorStateClass.MEASUREMENT, units=UnitOfTemperature.CELSIUS),
            "Supply Temp before re-heater": ModbusSensor(address=6201, scaling=0.1, deviceClass=SensorDeviceClass.TEMPERATURE, stateClass=SensorStateClass.MEASUREMENT, units=UnitOfTemperature.CELSIUS),
            "Supply Temp": ModbusSensor(address=6202, scaling=0.1, deviceClass=SensorDeviceClass.TEMPERATURE, stateClass=SensorStateClass.MEASUREMENT, units=UnitOfTemperature.CELSIUS),
            "Extract Temp": ModbusSensor(address=6203, scaling=0.1, deviceClass=SensorDeviceClass.TEMPERATURE, stateClass=SensorStateClass.MEASUREMENT, units=UnitOfTemperature.CELSIUS),
            "Exhaust Temp": ModbusSensor(address=6204, scaling=0.1, deviceClass=SensorDeviceClass.TEMPERATURE, stateClass=SensorStateClass.MEASUREMENT, units=UnitOfTemperature.CELSIUS),
            "Room_Temp": ModbusDatapoint(address=6205, scaling=0.1),
            "User Panel 1 Temp": ModbusSensor(address=6206, scaling=0.1, deviceClass=SensorDeviceClass.TEMPERATURE, stateClass=SensorStateClass.MEASUREMENT, units=UnitOfTemperature.CELSIUS),
            "User Panel 2 Temp": ModbusDatapoint(address=6207, scaling=0.1),
            "Water Radiator Temp": ModbusDatapoint(address=6208, scaling=0.1),
            "Pre-Heater Temp": ModbusDatapoint(address=6209, scaling=0.1),
            "External Fresh Air Temp": ModbusDatapoint(address=6210, scaling=0.1),
            "CO2 Unfiltered": ModbusDatapoint(address=6211),
            "CO2 Filtered": ModbusSensor(address=6212, deviceClass=SensorDeviceClass.CO2, stateClass=SensorStateClass.MEASUREMENT, units=UnitOfRatio.PARTS_PER_MILLION, enabledDefault=False),
            "Relative Humidity": ModbusSensor(address=6213, deviceClass=SensorDeviceClass.HUMIDITY, stateClass=SensorStateClass.MEASUREMENT, units=PERCENTAGE),
            "Absolute Humidity": ModbusSensor(address=6214, scaling=0.1, units="g/m³", icon="mdi:water"),
            "Absolute Humidity SP": ModbusDatapoint(address=6215, scaling=0.1),
            "VOC": ModbusDatapoint(address=6216),
            "Supply Pressure": ModbusDatapoint(address=6217),
            "Exhaust Pressure": ModbusDatapoint(address=6218),
            "Supply Flow": ModbusDatapoint(address=6219, scaling=3.6),
            "Exhaust Flow": ModbusDatapoint(address=6220, scaling=3.6),
        }

        # UNIT_STATUSES - Read
        self.Datapoints[GROUP_UNIT_STATUSES] = {
            "Unit_state": ModbusDatapoint(address=6300),
            "Speed_state": ModbusDatapoint(address=6301),
            "Supply Fan": ModbusSensor(address=6302, units=PERCENTAGE, icon="mdi:fan"),
            "Exhaust Fan": ModbusSensor(address=6303, units=PERCENTAGE, icon="mdi:fan"),
            "Supply_Fan_RPM": ModbusDatapoint(address=6304),
            "Exhaust_Fan_RPM": ModbusDatapoint(address=6305),
            "Heating Output": ModbusSensor(address=6316, units=PERCENTAGE, icon="mdi:radiator"),   
            "Heat Exchanger": ModbusSensor(address=6331, units=PERCENTAGE, icon="mdi:hvac"),         
        }

        # CONFIGURATION - Read/Write
        self.Datapoints[ModbusDefaultGroups.CONFIG] = {
            "Travelling Mode Speed Drop": ModbusNumber(address=5105, units=PERCENTAGE, min_value=0, max_value=20, step=1),
            "Fireplace Run Time": ModbusNumber(address=5103, units=UnitOfTime.MINUTES, min_value=0, max_value=60, step=1),
            "Fireplace Max Speed Difference": ModbusNumber(address=5104, units=PERCENTAGE, min_value=0, max_value=25, step=1),
            "Night Cooling": ModbusNumber(address=5163, units=None),
            "Night Cooling FreshAir Max": ModbusNumber(address=5164, scaling=0.1, deviceClass=NumberDeviceClass.TEMPERATURE, units=UnitOfTemperature.CELSIUS, min_value=0, max_value=25, step=0.1),
            "Night Cooling FreshAir Start": ModbusNumber(address=5165, scaling=0.1, deviceClass=NumberDeviceClass.TEMPERATURE, units=UnitOfTemperature.CELSIUS, min_value=0, max_value=25, step=0.1),
            "Night Cooling RoomTemp Start": ModbusNumber(address=5166, scaling=0.1, deviceClass=NumberDeviceClass.TEMPERATURE, units=UnitOfTemperature.CELSIUS, min_value=0, max_value=35, step=0.1),
            "Night Cooling SupplyTemp Min": ModbusNumber(address=5167, scaling=0.1, deviceClass=NumberDeviceClass.TEMPERATURE, units=UnitOfTemperature.CELSIUS, min_value=10, max_value=25, step=0.1),
            "Away Supply Speed": ModbusNumber(address=5301, units=PERCENTAGE, min_value=20, max_value=100, step=1),
            "Away Exhaust Speed": ModbusNumber(address=5302, units=PERCENTAGE, min_value=20, max_value=100, step=1),
            "Home Supply Speed": ModbusNumber(address=5303, units=PERCENTAGE, min_value=20, max_value=100, step=1),
            "Home Exhaust Speed": ModbusNumber(address=5304, units=PERCENTAGE, min_value=20, max_value=100, step=1),
            "Boost Supply Speed": ModbusNumber(address=5305, units=PERCENTAGE, min_value=20, max_value=100, step=1),
            "Boost Exhaust Speed": ModbusNumber(address=5306, units=PERCENTAGE, min_value=20, max_value=100, step=1),
            "Operating Mode": ModbusSelect(address=5000, options={0: "Stopped", 1: "Away", 2: "Home", 3: "Boost", 4: "Travel"}),
        }

        # UI datapoints that are calculated and not read directly over modbus
        self.Datapoints[GROUP_UI] = {
            "Current Alarms": ModbusSensor(icon="mdi:bell"),
            "Efficiency": ModbusSensor(units=PERCENTAGE, icon="mdi:percent"),
            "Efficiency Extract": ModbusSensor(units=PERCENTAGE, icon="mdi:percent"),
        }       

    def onAfterFirstRead(self):
        # Update device info
        self.model = self.Datapoints[GROUP_DEVICE_INFO]["Model Name"].value
        self.serial_number = self.Datapoints[GROUP_DEVICE_INFO]["Serial Number"].value

        a = self.Datapoints[GROUP_DEVICE_INFO]["FW Maj"].value
        b = self.Datapoints[GROUP_DEVICE_INFO]["FW Min"].value
        c = self.Datapoints[GROUP_DEVICE_INFO]["FW Build"].value
        self.sw_version = '{}.{}.{}'.format(a,b,c)

    def onAfterRead(self):
        # Calculate efficiency
        fresh = self.Datapoints[GROUP_SENSORS]["Fresh Air Temp"].value
        sup = self.Datapoints[GROUP_SENSORS]["Supply Temp before re-heater"].value
        extract = self.Datapoints[GROUP_SENSORS]["Extract Temp"].value
        exhaust = self.Datapoints[GROUP_SENSORS]["Exhaust Temp"].value

        try:
            efficiency = ((sup - fresh) / (extract - fresh)) * 100
            efficiency = max(0, min(100, efficiency))
            self.Datapoints[GROUP_UI]["Efficiency"].value = round(efficiency, 1)
        except ZeroDivisionError:
            self.Datapoints[GROUP_UI]["Efficiency"].value = 0
        try:
            efficiency = ((extract - exhaust) / (extract - fresh)) * 100
            efficiency = max(0, min(100, efficiency))
            self.Datapoints[GROUP_UI]["Efficiency Extract"].value = round(efficiency, 1)
        except ZeroDivisionError:
            self.Datapoints[GROUP_UI]["Efficiency Extract"].value = 0

        # Set alarms as attributes on Alarm-datapoint. This is done so that we don't
        # need to present all values in the UI
        alarms = self.Datapoints[GROUP_ALARMS]
        attrs = {}
        for (dataPointName, data) in alarms.items():
            if data.value:
                attrs.update({dataPointName:"ALARM"})
        alarms["Active Alarms"].attrs = attrs

        # Set alarm state on current alarms entity for summary
        active = sorted(attrs.keys())
        state = ", ".join(active) if active else "None"
        self.Datapoints[GROUP_UI]["Current Alarms"].value = state