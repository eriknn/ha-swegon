from typing import Type
from .coordinator import ModbusCoordinator
from .devices.datatypes import ModbusSensor, ModbusNumber, ModbusSelect, ModbusBinarySensor, ModbusSwitch, ModbusButton, ModbusDefaultGroups

def create_entities(coordinator:ModbusCoordinator , entity_cls: Type, entity_data_type: Type):
    entities = []

    for group, datapoints in coordinator._modbusDevice.Datapoints.items():
        if group == ModbusDefaultGroups.CONFIG:
            continue

        for key, datapoint in datapoints.items():
            if isinstance(datapoint, entity_data_type):
                entities.append(entity_cls(coordinator, group, key, datapoint))

    return entities