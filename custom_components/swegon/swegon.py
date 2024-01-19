from struct import pack, unpack
from dataclasses import dataclass

import logging
import math

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ModbusResponse
from pymodbus.transaction import ModbusSocketFramer

_LOGGER = logging.getLogger(__name__)

@dataclass
class Modbus_Datapoint:
    Address: int
    Scaling: float = None
    Value: float = 0

class Swegon:
    # The modbus registers are divided into logical groups.
    # This allows us to read multiple registers in one call.
    Statuses = {}
    Statuses["Op_Mode"] = Modbus_Datapoint(5000)
    Statuses["Fireplace_Mode"] = Modbus_Datapoint(5001)
    Statuses["Unused"] = Modbus_Datapoint(5002)
    Statuses["Traveling_Mode"] = Modbus_Datapoint(5003)    

    Setpoints = {}
    Setpoints["Temp_SP"] = Modbus_Datapoint(5100, 0.1)

    Device_Info = {}
    Device_Info["FW_Maj"] = Modbus_Datapoint(6000)
    Device_Info["FW_Min"] = Modbus_Datapoint(6001)
    Device_Info["FW_Build"] = Modbus_Datapoint(6002)
    Device_Info["Par_Maj"] = Modbus_Datapoint(6003) 
    Device_Info["Par_Min"] = Modbus_Datapoint(6004)
    Device_Info["Model_Name"] = Modbus_Datapoint(6007)   # 15 Bytes
    Device_Info["Serial_Number"] = Modbus_Datapoint(6023)   # 24 Bytes
    
    Sensors = {}
    Sensors["Fresh_T"] = Modbus_Datapoint(6200, 0.1)
    Sensors["Supply_T1"] = Modbus_Datapoint(6201, 0.1)
    Sensors["Supply_T2"] = Modbus_Datapoint(6202, 0.1)
    Sensors["Extract_T"] = Modbus_Datapoint(6203, 0.1)
    Sensors["Exhaust_T"] = Modbus_Datapoint(6204, 0.1)
    Sensors["Room_T"] = Modbus_Datapoint(6205, 0.1)
    Sensors["UP1_T"] = Modbus_Datapoint(6206, 0.1)
    Sensors["UP2_T"] = Modbus_Datapoint(6207, 0.1)
    Sensors["WR_T"] = Modbus_Datapoint(6208, 0.1)
    Sensors["PreHeat_T"] = Modbus_Datapoint(6209, 0.1)
    Sensors["ExtFresh_T"] = Modbus_Datapoint(6210, 0.1)
    Sensors["C02_Unf"] = Modbus_Datapoint(6211, 1.0)
    Sensors["CO2_Fil"] = Modbus_Datapoint(6212, 1.0)
    Sensors["RH"] = Modbus_Datapoint(6213, 1.0)
    Sensors["AH"] = Modbus_Datapoint(6214, 0.1)
    Sensors["AH_SP"] = Modbus_Datapoint(6215, 0.1)
    Sensors["VOC"] = Modbus_Datapoint(6216, 1.0)
    Sensors["Supp_P"] = Modbus_Datapoint(6217, 1.0)
    Sensors["Ex_P"] = Modbus_Datapoint(6218, 1.0)
    Sensors["Supp_Flow"] = Modbus_Datapoint(6219, 3.6)
    Sensors["Ex_Flow"] = Modbus_Datapoint(6220, 3.6)

    UnitStatuses = {}
    UnitStatuses["Unit_state"] = Modbus_Datapoint(6300)
    UnitStatuses["Speed_state"] = Modbus_Datapoint(6301)
    UnitStatuses["Supply_Fan"] = Modbus_Datapoint(6302)
    UnitStatuses["Exhaust_Fan"] = Modbus_Datapoint(6303)
    UnitStatuses["Supply_Fan_RPM"] = Modbus_Datapoint(6304)
    UnitStatuses["Exhaust_Fan_RPM"] = Modbus_Datapoint(6305)
    UnitStatuses["NotUsed1"] = Modbus_Datapoint(6306)
    UnitStatuses["NotUsed2"] = Modbus_Datapoint(6307)
    UnitStatuses["NotUsed3"] = Modbus_Datapoint(6308)
    UnitStatuses["NotUsed4"] = Modbus_Datapoint(6309)
    UnitStatuses["NotUsed5"] = Modbus_Datapoint(6310)
    UnitStatuses["NotUsed6"] = Modbus_Datapoint(6311)
    UnitStatuses["NotUsed7"] = Modbus_Datapoint(6312)
    UnitStatuses["NotUsed8"] = Modbus_Datapoint(6313)
    UnitStatuses["NotUsed9"] = Modbus_Datapoint(6314)
    UnitStatuses["Temp_SP"] = Modbus_Datapoint(6315)
    UnitStatuses["Heating_Output"] = Modbus_Datapoint(6316)
    #UnitStatuses["Rotor"] = Modbus_Datapoint(6233)

    _client = None

    def __init__(self, host, port):
        self._client = ModbusTcpClient(host, port)

    def connect(self):
        if not self._client.connected:
            _LOGGER.debug("Connecting to server!")
            self._client.connect()

    def disconnect(self):
        _LOGGER.debug("Disconnecting!")
        self._client.close()

    def getFW(self) -> str:
        a = self.Device_Info["FW_Maj"].Value
        b = self.Device_Info["FW_Min"].Value
        c = self.Device_Info["FW_Build"].Value
        return '{}.{}.{}'.format(a,b,c)

    def getModelName(self) -> str:
        name = ''.join(chr(value) for value in self.Device_Info["Model_Name"].Value)
        return name.rstrip('\x00')

    def getSerialNumber(self) -> str:
        serial = ''.join(chr(value) for value in self.Device_Info["Serial_Number"].Value)
        return serial.rstrip('\x00')

    async def readStatuses(self):
        # We read multiple holding registers in one message
        self.connect()

        response = self._client.read_holding_registers(5000,4)
        if response.isError():
            raise ModbusException('{}'.format(response))
        else:
            for (dataPointName, data), newVal in zip(self.Statuses.items(), response.registers):
                data.Value = newVal
        return True

    async def readSetpoints(self):
        # We read multiple holding registers in one message
        self.connect()

        response = self._client.read_holding_registers(5100,1)
        if response.isError():
            raise ModbusException('{}'.format(response))
        else:
            for (dataPointName, data), newVal in zip(self.Setpoints.items(), response.registers):
                data.Value = newVal * data.Scaling
        return True

    async def readDeviceInfo(self):
        # We read multiple holding registers in one message
        self.connect()

        response = self._client.read_holding_registers(6000,47)
        if response.isError():
            raise ModbusException('{}'.format(response))
        else:
            self.Device_Info["FW_Maj"].Value = response.registers[0]
            self.Device_Info["FW_Min"].Value = response.registers[1]
            self.Device_Info["FW_Build"].Value = response.registers[2]
            self.Device_Info["Par_Maj"].Value = response.registers[3]
            self.Device_Info["Par_Min"].Value = response.registers[4]
            self.Device_Info["Model_Name"].Value = response.registers[7:22]
            self.Device_Info["Serial_Number"].Value = response.registers[23:47]
        return True

    async def readSensors(self):
        # We read multiple holding registers in one message
        self.connect()

        response = self._client.read_holding_registers(6200,21)
        if response.isError():
            raise ModbusException('{}'.format(response))
        else:
            for (dataPointName, data), newVal in zip(self.Sensors.items(), response.registers):
                data.Value = newVal * data.Scaling
        return True

    async def readUnitStatuses(self):
        # We read multiple holding registers in one message
        self.connect()

        response = self._client.read_holding_registers(6300,17)
        if response.isError():
            raise ModbusException('{}'.format(response))
        else:
            for (dataPointName, data), newVal in zip(self.UnitStatuses.items(), response.registers):
                data.Value = newVal
        return True

    async def writeSetpoint(self, key, value) -> bool:
        # We write single holding registers
        self.connect()

        scaledVal = round(value/self.Setpoints[key].Scaling)
        response = self._client.write_register(self.Setpoints[key].Address, scaledVal)
        if response.isError():
            raise ModbusException('{}'.format(response))
        else:
            self.Setpoints[key].Value = value
        return True

    async def writeStatus(self, key, value) -> bool:
        # We write single holding registers
        _LOGGER.debug("Writing status: %s - %s", key, value)
        self.connect()

        response = self._client.write_register(self.Statuses[key].Address, value)
        if response.isError():
            raise ModbusException('{}'.format(response))
        else:
            self.Statuses[key].Value = value
        return True
