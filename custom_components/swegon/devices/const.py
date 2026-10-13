from enum import Enum

class ByteOrder(str, Enum):
    MSB = 'MSB'
    LSB = 'LSB'

class WordOrder(str, Enum):
    NORMAL = 'NORMAL'
    SWAP = 'SWAP'

class ModbusDataType(str, Enum):
    INT = 'int'
    UINT = 'uint'
    FLOAT = 'float'
    STRING1 = 'string1'
    STRING2 = 'string2'

class ModbusMode(Enum):
    NONE = 0                # Used for virtual data points
    COILS = 1               # Function codes 1/5/15
    DISCRETE_INPUTS = 2     # Function codes 2
    HOLDING = 3             # Function codes 3/6/16
    INPUT = 4               # Function codes 4

class ModbusPollMode(Enum):
    POLL_OFF = 0            # Values will not be read automatically
    POLL_ON = 1             # Values will be read each poll interval
    POLL_ONCE = 2           # Just read them once, for example for static configuration

