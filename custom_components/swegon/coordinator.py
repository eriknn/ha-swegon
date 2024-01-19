import async_timeout
import datetime as dt
import logging

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .swegon import Swegon

_LOGGER = logging.getLogger(__name__)

class SwegonCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, device, ip, port, scan_interval):
        """Initialize coordinator parent"""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Swegon CASA: " + device.name,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=dt.timedelta(seconds=scan_interval),
        )

        self._device = device
        self._swegonDevice = Swegon(ip, port)

        # Initialize states
        self._loaded = False
        self._measurements = None
        self._setpoints = None
        self._timestamp = dt.datetime(2024, 1, 1)
        
    async def _async_update_data(self):
        _LOGGER.debug("Coordinator updating data!!")

        """ Fetch data """
        try:
            async with async_timeout.timeout(20):
                if self._swegonDevice.Device_Info["FW_Maj"].Value == 0:
                    await self._swegonDevice.readDeviceInfo()
                if (dt.datetime.now() - self._timestamp) > dt.timedelta(hours=3):
                    await self._swegonDevice.readSetpoints() 
                    self._timestamp = dt.datetime.now()
                await self._swegonDevice.readSensors()
                await self._swegonDevice.readStatuses()
                await self._swegonDevice.readUnitStatuses()

                if not self._loaded:
                    await self._async_update_deviceInfo()
                    self._loaded = True
                
        except Exception as err:
            _LOGGER.debug("Failed when fetching data: %s", str(err))

    async def _async_update_deviceInfo(self) -> None:
        device_registry = dr.async_get(self.hass)
        device_registry.async_update_device(
            self.device_id,
            manufacturer="Swegon",
            model=self._swegonDevice.getModelName(),
            serial_number=self._swegonDevice.getSerialNumber(),
            sw_version=self._swegonDevice.getFW(),
        )
        _LOGGER.debug("Updated device data for: %s", self.devicename) 

    @property
    def device_id(self):
        return self._device.id

    @property
    def devicename(self):
        return self._device.name

    @property
    def identifiers(self):
        return self._device.identifiers    

    def get_value(self, key):
        if key in self._swegonDevice.Sensors:
            return self._swegonDevice.Sensors[key].Value
        elif key in self._swegonDevice.UnitStatuses:
            return self._swegonDevice.UnitStatuses[key].Value
        elif key in self._swegonDevice.Setpoints:
            return self._swegonDevice.Setpoints[key].Value
        elif key in self._swegonDevice.Statuses:
            return self._swegonDevice.Statuses[key].Value
        return None    

    async def write_value(self, key, value) -> bool:
        _LOGGER.debug("Write_Data: %s", key)
        try:
            if key in self._swegonDevice.Setpoints:
                await self._swegonDevice.writeSetpoint(key, value)
            elif key in self._swegonDevice.Statuses:
                await self._swegonDevice.writeStatus(key, value)
        except Exception as e:
            _LOGGER.debug("Not able to write command: %s", str(e))
            return False
