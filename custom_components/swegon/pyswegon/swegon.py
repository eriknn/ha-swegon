from dataclasses import dataclass

import logging

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

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

class Swegon():
    def __init__(self, device_module:str, host:str, port:int, slave_id:int):
        self._client = ModbusTcpClient(host=host, port=port)
        self._slave_id = slave_id

        # Load correct datapoints
        self.load_datapoints(device_module)


    def load_datapoints(self, device_module:str):
        module_name = f"{device_module.lower().replace(' ', '_')}"

        if module_name == 'casa_r4':
            from .devices.casa_r4 import CasaR4
            self.Datapoints = CasaR4().Datapoints
        elif module_name == 'casa_r15':
            from .devices.casa_r15 import CasaR15
            self.Datapoints = CasaR15().Datapoints
        else:
            self.Datapoints = {}

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
        response = self._client.read_input_registers(address=6000, count=47, device_id=self._slave_id)

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
            response = self._client.read_input_registers(address=first_address, count=n_reg, device_id=self._slave_id)
        elif mode == MODE_HOLDING:
            response = self._client.read_holding_registers(address=first_address, count=n_reg, device_id=self._slave_id)
            
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
            response = self._client.read_input_registers(address=self.Datapoints[group][key].Address, count=1, device_id=self._slave_id)
        elif mode == MODE_HOLDING:
            response = self._client.read_holding_registers(address=self.Datapoints[group][key].Address, count=1, device_id=self._slave_id)

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
        response = self._client.write_register(address=self.Datapoints[group][key].Address, value=scaledVal, device_id=self._slave_id)

        if response.isError():
            raise ModbusException('{}'.format(response))
        else:
            self.Datapoints[group][key].Value = value
