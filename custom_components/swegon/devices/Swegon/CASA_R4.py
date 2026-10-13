import logging
from .CASA_Base import Device as BaseDevice

_LOGGER = logging.getLogger(__name__)

class Device(BaseDevice):
    # Override static device information
    manufacturer="Swegon"

    # Override dynamic data
    def loadDatapoints(self):
        super().loadDatapoints() 