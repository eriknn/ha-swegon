import logging

from .casa_base import CasaBase
from ..swegon import Modbus_Datapoint
from ..swegon import COMMANDS,SETPOINTS,DEVICE_INFO,ALARMS,SENSORS,SENSORS2,VIRTUALSENSORS,UNIT_STATUSES,CONFIG

_LOGGER = logging.getLogger(__name__)

class CasaR15(CasaBase):
    def __init__(self):
        super().__init__()
        self.Datapoints[SETPOINTS]["Temp_SP"] = Modbus_Datapoint(5100, 1)

        _LOGGER.debug("Loaded datapoints for Swegon Casa R15")