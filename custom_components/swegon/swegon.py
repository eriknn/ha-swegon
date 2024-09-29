from dataclasses import dataclass

import logging

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ModbusResponse
from pymodbus.transaction import ModbusSocketFramer

_LOGGER = logging.getLogger(__name__)

@dataclass
class Modbus_Datapoint:
    Address: int
    Scaling: float = 1
    Value: float = 0

# ENUMS FOR GROUPS
COMMANDS = "Commands"
SETPOINTS = "Setpoints"
DEVICE_INFO = "Device_Info"
ALARMS = "Alarms"
SENSORS = "Sensors"
SENSORS2 = "Sensors2"
VIRTUALSENSORS = "VirtualSensors"
UNIT_STATUSES = "UnitStatuses"
CONFIG = "Config"

MODE_INPUT = 3
MODE_HOLDING = 4

class Swegon:
    # The modbus registers are divided into logical groups.
    # This allows us to read multiple registers in one call.

    # Base container
    Datapoints = {}

    # Read / Write - Holding registers
    Datapoints[COMMANDS] = {}
    Datapoints[COMMANDS]["Op_Mode"] = Modbus_Datapoint(5000)
    Datapoints[COMMANDS]["Fireplace_Mode"] = Modbus_Datapoint(5001)
    Datapoints[COMMANDS]["Unused"] = Modbus_Datapoint(5002)
    Datapoints[COMMANDS]["Travelling_Mode"] = Modbus_Datapoint(5003)    

    # Read / Write - Holding registers
    Datapoints[SETPOINTS] = {}
    Datapoints[SETPOINTS]["Temp_SP"] = Modbus_Datapoint(5100, 0.1)

    # Read only - Input registers
    Datapoints[DEVICE_INFO] = {}
    Datapoints[DEVICE_INFO]["FW_Maj"] = Modbus_Datapoint(6000)
    Datapoints[DEVICE_INFO]["FW_Min"] = Modbus_Datapoint(6001)
    Datapoints[DEVICE_INFO]["FW_Build"] = Modbus_Datapoint(6002)
    Datapoints[DEVICE_INFO]["Par_Maj"] = Modbus_Datapoint(6003) 
    Datapoints[DEVICE_INFO]["Par_Min"] = Modbus_Datapoint(6004)
    Datapoints[DEVICE_INFO]["Model_Name"] = Modbus_Datapoint(6007)   # 15 Bytes
    Datapoints[DEVICE_INFO]["Serial_Number"] = Modbus_Datapoint(6023)   # 24 Bytes

    # Read only - Input registers
    Datapoints[ALARMS] = {}
    Datapoints[ALARMS]["T1_Failure"] = Modbus_Datapoint(6100)
    Datapoints[ALARMS]["T2_Failure"] = Modbus_Datapoint(6101)
    Datapoints[ALARMS]["T3_Failure"] = Modbus_Datapoint(6102)
    Datapoints[ALARMS]["T4_Failure"] = Modbus_Datapoint(6103)
    Datapoints[ALARMS]["T5_Failure"] = Modbus_Datapoint(6104)
    Datapoints[ALARMS]["T6_Failure"] = Modbus_Datapoint(6105)
    Datapoints[ALARMS]["T7_Failure"] = Modbus_Datapoint(6106)
    Datapoints[ALARMS]["T8_Failure"] = Modbus_Datapoint(6107)
    Datapoints[ALARMS]["T1_Failure_Unconf"] = Modbus_Datapoint(6108)
    Datapoints[ALARMS]["T2_Failure_Unconf"] = Modbus_Datapoint(6109)
    Datapoints[ALARMS]["T3_Failure_Unconf"] = Modbus_Datapoint(6110)
    Datapoints[ALARMS]["T4_Failure_Unconf"] = Modbus_Datapoint(6111)
    Datapoints[ALARMS]["T5_Failure_Unconf"] = Modbus_Datapoint(6112)
    Datapoints[ALARMS]["T6_Failure_Unconf"] = Modbus_Datapoint(6113)
    Datapoints[ALARMS]["T7_Failure_Unconf"] = Modbus_Datapoint(6114)
    Datapoints[ALARMS]["T8_Failure_Unconf"] = Modbus_Datapoint(6115)
    Datapoints[ALARMS]["Afterheater_Failure"] = Modbus_Datapoint(6116)
    Datapoints[ALARMS]["Afterheater_Failure_Unconf"] = Modbus_Datapoint(6117)
    Datapoints[ALARMS]["Preheater_Failure"] = Modbus_Datapoint(6118)
    Datapoints[ALARMS]["Preheater_Failure_Unconf"] = Modbus_Datapoint(6119)
    Datapoints[ALARMS]["Freezing_Danger"] = Modbus_Datapoint(6120)    
    Datapoints[ALARMS]["Freezing_Danger_Unconf"] = Modbus_Datapoint(6121)
    Datapoints[ALARMS]["Internal_Error"] = Modbus_Datapoint(6122)
    Datapoints[ALARMS]["Internal_Error_Unconf"] = Modbus_Datapoint(6123)
    Datapoints[ALARMS]["Supply_Fan_Failure"] = Modbus_Datapoint(6124)
    Datapoints[ALARMS]["Supply_Fan_Failure_Unconf"] = Modbus_Datapoint(6125)
    Datapoints[ALARMS]["Exhaust_Fan_Failure"] = Modbus_Datapoint(6126)
    Datapoints[ALARMS]["Exhaust_Fan_Failure_Unconf"] = Modbus_Datapoint(6127)
    Datapoints[ALARMS]["Service_Info"] = Modbus_Datapoint(6128)
    Datapoints[ALARMS]["Filter_Guard_Info"] = Modbus_Datapoint(6129)
    Datapoints[ALARMS]["Emergency_Stop"] = Modbus_Datapoint(6130)
    Datapoints[ALARMS]["Active_Alarms"] = Modbus_Datapoint(6131)
    Datapoints[ALARMS]["Info_Unconf"] = Modbus_Datapoint(6132)

    # Read only - Input registers
    Datapoints[SENSORS] = {}
    Datapoints[SENSORS]["Fresh_Temp"] = Modbus_Datapoint(6200, 0.1)
    Datapoints[SENSORS]["Supply_Temp1"] = Modbus_Datapoint(6201, 0.1)
    Datapoints[SENSORS]["Supply_Temp2"] = Modbus_Datapoint(6202, 0.1)
    Datapoints[SENSORS]["Extract_Temp"] = Modbus_Datapoint(6203, 0.1)
    Datapoints[SENSORS]["Exhaust_Temp"] = Modbus_Datapoint(6204, 0.1)
    Datapoints[SENSORS]["Room_Temp"] = Modbus_Datapoint(6205, 0.1)
    Datapoints[SENSORS]["UP1_Temp"] = Modbus_Datapoint(6206, 0.1)
    Datapoints[SENSORS]["UP2_Temp"] = Modbus_Datapoint(6207, 0.1)
    Datapoints[SENSORS]["WR_Temp"] = Modbus_Datapoint(6208, 0.1)
    Datapoints[SENSORS]["PreHeat_Temp"] = Modbus_Datapoint(6209, 0.1)
    Datapoints[SENSORS]["ExtFresh_Temp"] = Modbus_Datapoint(6210, 0.1)
    Datapoints[SENSORS]["C02_Unf"] = Modbus_Datapoint(6211, 1.0)
    Datapoints[SENSORS]["CO2_Fil"] = Modbus_Datapoint(6212, 1.0)
    Datapoints[SENSORS]["RH"] = Modbus_Datapoint(6213, 1.0)
    Datapoints[SENSORS]["AH"] = Modbus_Datapoint(6214, 0.1)
    Datapoints[SENSORS]["AH_SP"] = Modbus_Datapoint(6215, 0.1)
    Datapoints[SENSORS]["VOC"] = Modbus_Datapoint(6216, 1.0)
    Datapoints[SENSORS]["Supply_Pressure"] = Modbus_Datapoint(6217, 1.0)
    Datapoints[SENSORS]["Exhaust_Pressure"] = Modbus_Datapoint(6218, 1.0)
    Datapoints[SENSORS]["Supply_Flow"] = Modbus_Datapoint(6219, 3.6)
    Datapoints[SENSORS]["Exhaust_Flow"] = Modbus_Datapoint(6220, 3.6)

    # Read only - Input registers
    Datapoints[SENSORS2] = {}
    Datapoints[SENSORS2]["Heat_Exchanger"] = Modbus_Datapoint(6233, 1.0)  

    # Virtual sensors (calculated)
    Datapoints[VIRTUALSENSORS] = {}
    Datapoints[VIRTUALSENSORS]["Efficiency"] = Modbus_Datapoint(0, 1)  

    # Read only - Input registers
    Datapoints[UNIT_STATUSES] = {}
    Datapoints[UNIT_STATUSES]["Unit_state"] = Modbus_Datapoint(6300)
    Datapoints[UNIT_STATUSES]["Speed_state"] = Modbus_Datapoint(6301)
    Datapoints[UNIT_STATUSES]["Supply_Fan"] = Modbus_Datapoint(6302)
    Datapoints[UNIT_STATUSES]["Exhaust_Fan"] = Modbus_Datapoint(6303)
    Datapoints[UNIT_STATUSES]["Supply_Fan_RPM"] = Modbus_Datapoint(6304)
    Datapoints[UNIT_STATUSES]["Exhaust_Fan_RPM"] = Modbus_Datapoint(6305)
    Datapoints[UNIT_STATUSES]["NotUsed1"] = Modbus_Datapoint(6306)
    Datapoints[UNIT_STATUSES]["NotUsed2"] = Modbus_Datapoint(6307)
    Datapoints[UNIT_STATUSES]["NotUsed3"] = Modbus_Datapoint(6308)
    Datapoints[UNIT_STATUSES]["NotUsed4"] = Modbus_Datapoint(6309)
    Datapoints[UNIT_STATUSES]["NotUsed5"] = Modbus_Datapoint(6310)
    Datapoints[UNIT_STATUSES]["NotUsed6"] = Modbus_Datapoint(6311)
    Datapoints[UNIT_STATUSES]["NotUsed7"] = Modbus_Datapoint(6312)
    Datapoints[UNIT_STATUSES]["NotUsed8"] = Modbus_Datapoint(6313)
    Datapoints[UNIT_STATUSES]["NotUsed9"] = Modbus_Datapoint(6314)
    Datapoints[UNIT_STATUSES]["Temp_SP2"] = Modbus_Datapoint(6315)
    Datapoints[UNIT_STATUSES]["Heating_Output"] = Modbus_Datapoint(6316)

    # Read / Write - Holding registers
    Datapoints[CONFIG] = {}
    Datapoints[CONFIG]["Reset_Alarms"] = Modbus_Datapoint(5406)                     #5406
    Datapoints[CONFIG]["Travelling_Mode_Speed_Drop"] = Modbus_Datapoint(5105)       #5105  
    Datapoints[CONFIG]["Fireplace_Run_Time"] = Modbus_Datapoint(5103)               #5103
    Datapoints[CONFIG]["Fireplace_Max_Speed_Difference"] = Modbus_Datapoint(5104)   #5104
    Datapoints[CONFIG]["Night_Cooling"] = Modbus_Datapoint(5163)                    #5163
    Datapoints[CONFIG]["Night_Cooling_FreshAir_Max"] = Modbus_Datapoint(5164)       #5164
    Datapoints[CONFIG]["Night_Cooling_FreshAir_Start"] = Modbus_Datapoint(5165)     #5165
    Datapoints[CONFIG]["Night_Cooling_RoomTemp_Start"] = Modbus_Datapoint(5166)     #5166
    Datapoints[CONFIG]["Night_Cooling_SupplyTemp_Min"] = Modbus_Datapoint(5167)     #5167

    def __init__(self, host, port, slave_id):
        self._client = ModbusTcpClient(host, port)
        self._slave_id = slave_id
        
    def twos_complement(self, number) -> int:
        if number >> 15:
            return -((number^0xFFFF) + 1)
        else:
            return number

    def getMode(self, group) -> int:
        # Used to determine if a group is holding registers or input registers
        if group in (COMMANDS, SETPOINTS, CONFIG):
            return MODE_HOLDING
        elif group in (DEVICE_INFO, ALARMS, SENSORS, SENSORS2, UNIT_STATUSES):
            return MODE_INPUT
        else:
            return MODE_INPUT     

    """ ******************************************************* """
    """ **************** GET COMPOSITE VALUES ***************** """
    """ ******************************************************* """
    def getFW(self) -> str:
        a = self.Datapoints[DEVICE_INFO]["FW_Maj"].Value
        b = self.Datapoints[DEVICE_INFO]["FW_Min"].Value
        c = self.Datapoints[DEVICE_INFO]["FW_Build"].Value
        return '{}.{}.{}'.format(a,b,c)

    def getModelName(self) -> str:
        name = ''.join(chr(value) for value in self.Datapoints[DEVICE_INFO]["Model_Name"].Value)
        return name.rstrip('\x00')

    def getSerialNumber(self) -> str:
        serial = ''.join(chr(value) for value in self.Datapoints[DEVICE_INFO]["Serial_Number"].Value)
        return serial.rstrip('\x00')
    
    def calcVirtualSensors(self):
        fresh = self.Datapoints[SENSORS]["Fresh_Temp"].Value        # Outside temp
        sup = self.Datapoints[SENSORS]["Supply_Temp1"].Value        # Temp before heater
        extract = self.Datapoints[SENSORS]["Extract_Temp"].Value    # Extract temp
        efficiency = ((sup - fresh) / (extract - fresh)) * 100
        self.Datapoints[VIRTUALSENSORS]["Efficiency"].Value = round(efficiency, 1)

    """ ******************************************************* """
    """ **************** READ GROUP OF VALUES ***************** """
    """ ******************************************************* """
    async def readCommands(self):
        await self.readGroup(COMMANDS)

    async def readSetpoints(self):
        await self.readGroup(SETPOINTS)

    async def readDeviceInfo(self):
        # We read multiple input registers in one message
        response = self._client.read_input_registers(6000,47,self._slave_id)
        if response.isError():
            raise ModbusException('{}'.format(response))
        else:
            self.Datapoints[DEVICE_INFO]["FW_Maj"].Value = response.registers[0]
            self.Datapoints[DEVICE_INFO]["FW_Min"].Value = response.registers[1]
            self.Datapoints[DEVICE_INFO]["FW_Build"].Value = response.registers[2]
            self.Datapoints[DEVICE_INFO]["Par_Maj"].Value = response.registers[3]
            self.Datapoints[DEVICE_INFO]["Par_Min"].Value = response.registers[4]
            self.Datapoints[DEVICE_INFO]["Model_Name"].Value = response.registers[7:22]
            self.Datapoints[DEVICE_INFO]["Serial_Number"].Value = response.registers[23:47]

    async def readAlarms(self):
        await self.readGroup(ALARMS)

    async def readSensors(self):
        await self.readGroup(SENSORS)
        await self.readGroup(SENSORS2)
        self.calcVirtualSensors()

    async def readUnitStatuses(self):
        await self.readGroup(UNIT_STATUSES)

    """ ******************************************************* """
    """ ******************** READ GROUP *********************** """
    """ ******************************************************* """
    async def readGroup(self, group):
        # We read multiple registers in one message
        _LOGGER.debug("Reading group: %s", group)
        n_reg = len(self.Datapoints[group])
        first_key = next(iter(self.Datapoints[group]))
        first_address = self.Datapoints[group][first_key].Address
        
        mode = self.getMode(group)
        if mode == MODE_INPUT:
            response = self._client.read_input_registers(first_address,n_reg,self._slave_id)
        elif mode == MODE_HOLDING:
            response = self._client.read_holding_registers(first_address,n_reg,self._slave_id)
            
        if response.isError():
            raise ModbusException('{}'.format(response))
        else:
            for (dataPointName, data), newVal in zip(self.Datapoints[group].items(), response.registers):
                newVal_2 = self.twos_complement(newVal)
                if data.Scaling == 1.0:
                    data.Value = newVal_2
                else:
                    data.Value = newVal_2 * data.Scaling
                
    """ ******************************************************* """
    """ **************** READ SINGLE VALUE ******************** """
    """ ******************************************************* """
    async def readValue(self, group, key):
        # We read single register
        _LOGGER.debug("Reading value: %s - %s", group, key)

        mode = self.getMode(group)
        if mode == MODE_INPUT:
            response = self._client.read_input_registers(self.Datapoints[group][key].Address,1,self._slave_id)
        elif mode == MODE_HOLDING:
            response = self._client.read_holding_registers(self.Datapoints[group][key].Address,1,self._slave_id)

        if response.isError():
            raise ModbusException('{}'.format(response))
        else:
            newVal_2 = self.twos_complement(response.registers[0])
            self.Datapoints[group][key].Value = newVal_2 * self.Datapoints[group][key].Scaling

    """ ******************************************************* """
    """ **************** WRITE SINGLE VALUE ******************* """
    """ ******************************************************* """
    async def writeValue(self, group, key, value):
        # We write single holding register
        _LOGGER.debug("Writing value: %s - %s - %s", group, key, value)
        scaledVal = round(value/self.Datapoints[group][key].Scaling)
        scaledVal = self.twos_complement(scaledVal)
        response = self._client.write_register(self.Datapoints[group][key].Address, scaledVal, self._slave_id)
        if response.isError():
            raise ModbusException('{}'.format(response))
        else:
            self.Datapoints[group][key].Value = value