import logging

from ..swegon import Modbus_Datapoint
from ..swegon import COMMANDS,SETPOINTS,DEVICE_INFO,ALARMS,SENSORS,SENSORS2,VIRTUALSENSORS,UNIT_STATUSES,CONFIG

_LOGGER = logging.getLogger(__name__)

class CasaBase:
    def __init__(self):
        self.Datapoints = {}

        # Read / Write - Holding registers
        self.Datapoints[COMMANDS] = {}
        self.Datapoints[COMMANDS]["Op_Mode"] = Modbus_Datapoint(5000)
        self.Datapoints[COMMANDS]["Fireplace_Mode"] = Modbus_Datapoint(5001)
        self.Datapoints[COMMANDS]["Unused"] = Modbus_Datapoint(5002)
        self.Datapoints[COMMANDS]["Travelling_Mode"] = Modbus_Datapoint(5003)    

        # Read / Write - Holding registers
        self.Datapoints[SETPOINTS] = {}
        self.Datapoints[SETPOINTS]["Temp_SP"] = Modbus_Datapoint(5100, 0.1)

        # Read only - Input registers
        self.Datapoints[DEVICE_INFO] = {}
        self.Datapoints[DEVICE_INFO]["FW_Maj"] = Modbus_Datapoint(6000)
        self.Datapoints[DEVICE_INFO]["FW_Min"] = Modbus_Datapoint(6001)
        self.Datapoints[DEVICE_INFO]["FW_Build"] = Modbus_Datapoint(6002)
        self.Datapoints[DEVICE_INFO]["Par_Maj"] = Modbus_Datapoint(6003) 
        self.Datapoints[DEVICE_INFO]["Par_Min"] = Modbus_Datapoint(6004)
        self.Datapoints[DEVICE_INFO]["Model_Name"] = Modbus_Datapoint(6007)   # 15 Bytes
        self.Datapoints[DEVICE_INFO]["Serial_Number"] = Modbus_Datapoint(6023)   # 24 Bytes

        # Read only - Input registers
        self.Datapoints[ALARMS] = {}
        self.Datapoints[ALARMS]["T1_Failure"] = Modbus_Datapoint(6100)
        self.Datapoints[ALARMS]["T2_Failure"] = Modbus_Datapoint(6101)
        self.Datapoints[ALARMS]["T3_Failure"] = Modbus_Datapoint(6102)
        self.Datapoints[ALARMS]["T4_Failure"] = Modbus_Datapoint(6103)
        self.Datapoints[ALARMS]["T5_Failure"] = Modbus_Datapoint(6104)
        self.Datapoints[ALARMS]["T6_Failure"] = Modbus_Datapoint(6105)
        self.Datapoints[ALARMS]["T7_Failure"] = Modbus_Datapoint(6106)
        self.Datapoints[ALARMS]["T8_Failure"] = Modbus_Datapoint(6107)
        self.Datapoints[ALARMS]["T1_Failure_Unconf"] = Modbus_Datapoint(6108)
        self.Datapoints[ALARMS]["T2_Failure_Unconf"] = Modbus_Datapoint(6109)
        self.Datapoints[ALARMS]["T3_Failure_Unconf"] = Modbus_Datapoint(6110)
        self.Datapoints[ALARMS]["T4_Failure_Unconf"] = Modbus_Datapoint(6111)
        self.Datapoints[ALARMS]["T5_Failure_Unconf"] = Modbus_Datapoint(6112)
        self.Datapoints[ALARMS]["T6_Failure_Unconf"] = Modbus_Datapoint(6113)
        self.Datapoints[ALARMS]["T7_Failure_Unconf"] = Modbus_Datapoint(6114)
        self.Datapoints[ALARMS]["T8_Failure_Unconf"] = Modbus_Datapoint(6115)
        self.Datapoints[ALARMS]["Afterheater_Failure"] = Modbus_Datapoint(6116)
        self.Datapoints[ALARMS]["Afterheater_Failure_Unconf"] = Modbus_Datapoint(6117)
        self.Datapoints[ALARMS]["Preheater_Failure"] = Modbus_Datapoint(6118)
        self.Datapoints[ALARMS]["Preheater_Failure_Unconf"] = Modbus_Datapoint(6119)
        self.Datapoints[ALARMS]["Freezing_Danger"] = Modbus_Datapoint(6120)    
        self.Datapoints[ALARMS]["Freezing_Danger_Unconf"] = Modbus_Datapoint(6121)
        self.Datapoints[ALARMS]["Internal_Error"] = Modbus_Datapoint(6122)
        self.Datapoints[ALARMS]["Internal_Error_Unconf"] = Modbus_Datapoint(6123)
        self.Datapoints[ALARMS]["Supply_Fan_Failure"] = Modbus_Datapoint(6124)
        self.Datapoints[ALARMS]["Supply_Fan_Failure_Unconf"] = Modbus_Datapoint(6125)
        self.Datapoints[ALARMS]["Exhaust_Fan_Failure"] = Modbus_Datapoint(6126)
        self.Datapoints[ALARMS]["Exhaust_Fan_Failure_Unconf"] = Modbus_Datapoint(6127)
        self.Datapoints[ALARMS]["Service_Info"] = Modbus_Datapoint(6128)
        self.Datapoints[ALARMS]["Filter_Guard_Info"] = Modbus_Datapoint(6129)
        self.Datapoints[ALARMS]["Emergency_Stop"] = Modbus_Datapoint(6130)
        self.Datapoints[ALARMS]["Active_Alarms"] = Modbus_Datapoint(6131)
        self.Datapoints[ALARMS]["Info_Unconf"] = Modbus_Datapoint(6132)

        # Read only - Input registers
        self.Datapoints[SENSORS] = {}
        self.Datapoints[SENSORS]["Fresh_Temp"] = Modbus_Datapoint(6200, 0.1)
        self.Datapoints[SENSORS]["Supply_Temp1"] = Modbus_Datapoint(6201, 0.1)
        self.Datapoints[SENSORS]["Supply_Temp2"] = Modbus_Datapoint(6202, 0.1)
        self.Datapoints[SENSORS]["Extract_Temp"] = Modbus_Datapoint(6203, 0.1)
        self.Datapoints[SENSORS]["Exhaust_Temp"] = Modbus_Datapoint(6204, 0.1)
        self.Datapoints[SENSORS]["Room_Temp"] = Modbus_Datapoint(6205, 0.1)
        self.Datapoints[SENSORS]["UP1_Temp"] = Modbus_Datapoint(6206, 0.1)
        self.Datapoints[SENSORS]["UP2_Temp"] = Modbus_Datapoint(6207, 0.1)
        self.Datapoints[SENSORS]["WR_Temp"] = Modbus_Datapoint(6208, 0.1)
        self.Datapoints[SENSORS]["PreHeat_Temp"] = Modbus_Datapoint(6209, 0.1)
        self.Datapoints[SENSORS]["ExtFresh_Temp"] = Modbus_Datapoint(6210, 0.1)
        self.Datapoints[SENSORS]["C02_Unf"] = Modbus_Datapoint(6211, 1.0)
        self.Datapoints[SENSORS]["CO2_Fil"] = Modbus_Datapoint(6212, 1.0)
        self.Datapoints[SENSORS]["RH"] = Modbus_Datapoint(6213, 1.0)
        self.Datapoints[SENSORS]["AH"] = Modbus_Datapoint(6214, 0.1)
        self.Datapoints[SENSORS]["AH_SP"] = Modbus_Datapoint(6215, 0.1)
        self.Datapoints[SENSORS]["VOC"] = Modbus_Datapoint(6216, 1.0)
        self.Datapoints[SENSORS]["Supply_Pressure"] = Modbus_Datapoint(6217, 1.0)
        self.Datapoints[SENSORS]["Exhaust_Pressure"] = Modbus_Datapoint(6218, 1.0)
        self.Datapoints[SENSORS]["Supply_Flow"] = Modbus_Datapoint(6219, 3.6)
        self.Datapoints[SENSORS]["Exhaust_Flow"] = Modbus_Datapoint(6220, 3.6)

        # Read only - Input registers
        self.Datapoints[SENSORS2] = {}
        self.Datapoints[SENSORS2]["Heat_Exchanger"] = Modbus_Datapoint(6233, 1.0)  

        # Virtual sensors (calculated)
        self.Datapoints[VIRTUALSENSORS] = {}
        self.Datapoints[VIRTUALSENSORS]["Efficiency"] = Modbus_Datapoint(0, 1)  

        # Read only - Input registers
        self.Datapoints[UNIT_STATUSES] = {}
        self.Datapoints[UNIT_STATUSES]["Unit_state"] = Modbus_Datapoint(6300)
        self.Datapoints[UNIT_STATUSES]["Speed_state"] = Modbus_Datapoint(6301)
        self.Datapoints[UNIT_STATUSES]["Supply_Fan"] = Modbus_Datapoint(6302)
        self.Datapoints[UNIT_STATUSES]["Exhaust_Fan"] = Modbus_Datapoint(6303)
        self.Datapoints[UNIT_STATUSES]["Supply_Fan_RPM"] = Modbus_Datapoint(6304)
        self.Datapoints[UNIT_STATUSES]["Exhaust_Fan_RPM"] = Modbus_Datapoint(6305)
        self.Datapoints[UNIT_STATUSES]["NotUsed1"] = Modbus_Datapoint(6306)
        self.Datapoints[UNIT_STATUSES]["NotUsed2"] = Modbus_Datapoint(6307)
        self.Datapoints[UNIT_STATUSES]["NotUsed3"] = Modbus_Datapoint(6308)
        self.Datapoints[UNIT_STATUSES]["NotUsed4"] = Modbus_Datapoint(6309)
        self.Datapoints[UNIT_STATUSES]["NotUsed5"] = Modbus_Datapoint(6310)
        self.Datapoints[UNIT_STATUSES]["NotUsed6"] = Modbus_Datapoint(6311)
        self.Datapoints[UNIT_STATUSES]["NotUsed7"] = Modbus_Datapoint(6312)
        self.Datapoints[UNIT_STATUSES]["NotUsed8"] = Modbus_Datapoint(6313)
        self.Datapoints[UNIT_STATUSES]["NotUsed9"] = Modbus_Datapoint(6314)
        self.Datapoints[UNIT_STATUSES]["Temp_SP2"] = Modbus_Datapoint(6315)
        self.Datapoints[UNIT_STATUSES]["Heating_Output"] = Modbus_Datapoint(6316)

        # Read / Write - Holding registers
        self.Datapoints[CONFIG] = {}
        self.Datapoints[CONFIG]["Reset_Alarms"] = Modbus_Datapoint(5406)                     #5406
        self.Datapoints[CONFIG]["Travelling_Mode_Speed_Drop"] = Modbus_Datapoint(5105)       #5105  
        self.Datapoints[CONFIG]["Fireplace_Run_Time"] = Modbus_Datapoint(5103)               #5103
        self.Datapoints[CONFIG]["Fireplace_Max_Speed_Difference"] = Modbus_Datapoint(5104)   #5104
        self.Datapoints[CONFIG]["Night_Cooling"] = Modbus_Datapoint(5163)                    #5163
        self.Datapoints[CONFIG]["Night_Cooling_FreshAir_Max"] = Modbus_Datapoint(5164)       #5164
        self.Datapoints[CONFIG]["Night_Cooling_FreshAir_Start"] = Modbus_Datapoint(5165)     #5165
        self.Datapoints[CONFIG]["Night_Cooling_RoomTemp_Start"] = Modbus_Datapoint(5166)     #5166
        self.Datapoints[CONFIG]["Night_Cooling_SupplyTemp_Min"] = Modbus_Datapoint(5167)     #5167

        _LOGGER.debug("Loaded base datapoints for Swegon Casa")