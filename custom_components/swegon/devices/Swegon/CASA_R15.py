import logging
from .CASA_Base import GROUP_SETPOINTS, Device as BaseDevice

_LOGGER = logging.getLogger(__name__)

class Device(BaseDevice):
    # Override static device information
    model="CASA R15"

    def loadDatapoints(self):
        super().loadDatapoints() 

        # Modify datapoints    
        self.Datapoints[GROUP_SETPOINTS]["Temperature Setpoint"].scaling = 1