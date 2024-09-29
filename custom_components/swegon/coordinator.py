import async_timeout
import datetime as dt
import logging

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .swegon import Swegon

_LOGGER = logging.getLogger(__name__)

class SwegonCoordinator(DataUpdateCoordinator):
    _fast_poll_enabled = False
    _fast_poll_count = 0
    _normal_poll_interval = 60
    _fast_poll_interval = 10
    
    def __init__(self, hass, device, ip, port, slave_id, scan_interval, scan_interval_fast):
        """Initialize coordinator parent"""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Swegon CASA: " + device.name,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=dt.timedelta(seconds=scan_interval),
        )

        self._normal_poll_interval = scan_interval
        self._fast_poll_interval = scan_interval_fast

        self._device = device
        self._swegonDevice = Swegon(ip, port, slave_id)

        # Initialize states
        self._measurements = None
        self._setpoints = None
        self._timestamp = dt.datetime(2024, 1, 1)

        # Storage for config selection
        self.config_selection = 0

        # Callback to entities
        self._update_callbacks = {}

    @property
    def device_id(self):
        return self._device.id

    @property
    def devicename(self):
        return self._device.name

    @property
    def identifiers(self):
        return self._device.identifiers

    def setFastPollMode(self):
        _LOGGER.debug("Enabling fast poll mode")
        self._fast_poll_enabled = True
        self._fast_poll_count = 0
        self.update_interval = dt.timedelta(seconds=self._fast_poll_interval)
        self._schedule_refresh()

    def setNormalPollMode(self):
        _LOGGER.debug("Enabling normal poll mode")
        self._fast_poll_enabled = False
        self.update_interval = dt.timedelta(seconds=self._normal_poll_interval)


    async def _async_update_data(self):
        _LOGGER.debug("Coordinator updating data!!")

        """ Counter for fast polling """
        if self._fast_poll_enabled:
            self._fast_poll_count += 1
            if self._fast_poll_count > 5:
                self.setNormalPollMode()

        """ Fetch data """
        try:
            async with async_timeout.timeout(20):
                if self._swegonDevice.Datapoints["Device_Info"]["FW_Maj"].Value == 0:
                    await self._swegonDevice.readDeviceInfo()
                    await self._async_update_deviceInfo()
                if (dt.datetime.now() - self._timestamp) > dt.timedelta(hours=3):
                    await self._swegonDevice.readSetpoints() 
                    self._timestamp = dt.datetime.now()
                await self._swegonDevice.readAlarms()
                await self._swegonDevice.readSensors()
                await self._swegonDevice.readCommands()
                await self._swegonDevice.readUnitStatuses()
                
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

    def registerOnUpdateCallback(self, entity, callbackfunc):
        self._update_callbacks.update({entity: callbackfunc})

    async def config_select(self, key, value):
        _LOGGER.debug("Selected: %s", key)

        self.config_selection = value
        try:
            await self._swegonDevice.readValue("Config", key)
        finally:
            await self._update_callbacks["Config_Value"](key)

    def get_config_options(self):
        configs = self._swegonDevice.Datapoints["Config"]
        options = {}
        for i, config in enumerate(configs):
            options.update({i:config})
        return options

    def get_value(self, group, key):
        if group in self._swegonDevice.Datapoints:
            if key in self._swegonDevice.Datapoints[group]:
                return self._swegonDevice.Datapoints[group][key].Value
        return None

    async def write_value(self, group, key, value) -> bool:
        _LOGGER.debug("Write_Data: %s - %s - %s", group, key, value)
        await self._swegonDevice.writeValue(group, key, value)
        self.setFastPollMode()
