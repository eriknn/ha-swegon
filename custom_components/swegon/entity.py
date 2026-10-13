"""Base entity class for Modbus Devices integration."""
import logging

from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .devices.datatypes import ModbusGroup, ModbusDatapoint

_LOGGER = logging.getLogger(__name__)

class ModbusBaseEntity(CoordinatorEntity):
    """Modbus base entity class."""

    def __init__(self, coordinator, group:ModbusGroup, key:str, modbusDataPoint:ModbusDatapoint):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)

        """Generic Entity properties"""
        self._attr_entity_category = modbusDataPoint.entity_data.category
        self._attr_icon = modbusDataPoint.entity_data.icon
        self._attr_name = "{} {}".format(self.coordinator.devicename, key)
        self._attr_unique_id = "{}-{}".format(self.coordinator.device_id, self.name)
        self._attr_device_info = DeviceInfo(identifiers=self.coordinator.identifiers)
        self._attr_entity_registry_enabled_default = modbusDataPoint.entity_data.enabledDefault
        
        """Store this entities keys."""
        self._group = group
        self._key = key

        self.modbusDataPoint = modbusDataPoint
        self._loadEntitySettings()

    # Override by subslasses
    def _loadEntitySettings(self):
        pass

    @property
    def extra_state_attributes(self):
        """Return entity-specific state attributes."""
        attrs = self.coordinator.get_attrs(self._group, self._key)
        return attrs if attrs is not None else {}

    def toggle_entity_visibility(self, hass, visible: bool):
        """Hide or show this entity on the device page at runtime."""
        ent_reg = er.async_get(hass)

        if visible:
            # Restore original device_id
            ent_reg.async_update_entity(self.entity_id, device_id=self.coordinator.device_id)
        else:
            # Detach from device
            ent_reg.async_update_entity(self.entity_id, device_id=None)

    def rename(self, hass, name: str):
        ent_reg = er.async_get(hass)
        ent_reg.async_update_entity(self.entity_id, name=name)