import logging

from .casa_base import CasaBase
from ..swegon import Modbus_Datapoint
from ..swegon import COMMANDS,SETPOINTS,DEVICE_INFO,ALARMS,SENSORS,SENSORS2,VIRTUALSENSORS,UNIT_STATUSES,CONFIG

_LOGGER = logging.getLogger(__name__)

class CasaR4(CasaBase):
    def __init__(self):
        super().__init__()

        _LOGGER.debug("Loaded datapoints for Swegon Casa R4")