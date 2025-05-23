"""Support for Vson binary sensors."""

from __future__ import annotations

from .vson_ble import (
    BinarySensorDeviceClass as VsonBinarySensorDeviceClass,
    SensorUpdate,
)

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataUpdate,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.sensor import sensor_device_info_to_hass_device_info

from .coordinator import VsonPassiveBluetoothDataProcessor
from .device import device_key_to_bluetooth_entity_key
from .types import VsonConfigEntry

BINARY_SENSOR_DESCRIPTIONS = {
    VsonBinarySensorDeviceClass.BATTERY: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.BATTERY,
        device_class=BinarySensorDeviceClass.BATTERY,
    ),
    VsonBinarySensorDeviceClass.BATTERY_CHARGING: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.BATTERY_CHARGING,
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
    ),
    VsonBinarySensorDeviceClass.CO: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.CO,
        device_class=BinarySensorDeviceClass.CO,
    ),
    VsonBinarySensorDeviceClass.COLD: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.COLD,
        device_class=BinarySensorDeviceClass.COLD,
    ),
    VsonBinarySensorDeviceClass.CONNECTIVITY: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.CONNECTIVITY,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    VsonBinarySensorDeviceClass.DOOR: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.DOOR,
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    VsonBinarySensorDeviceClass.HEAT: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.HEAT,
        device_class=BinarySensorDeviceClass.HEAT,
    ),
    VsonBinarySensorDeviceClass.GARAGE_DOOR: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.GARAGE_DOOR,
        device_class=BinarySensorDeviceClass.GARAGE_DOOR,
    ),
    VsonBinarySensorDeviceClass.GAS: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.GAS,
        device_class=BinarySensorDeviceClass.GAS,
    ),
    VsonBinarySensorDeviceClass.GENERIC: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.GENERIC,
    ),
    VsonBinarySensorDeviceClass.LIGHT: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.LIGHT,
        device_class=BinarySensorDeviceClass.LIGHT,
    ),
    VsonBinarySensorDeviceClass.LOCK: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.LOCK,
        device_class=BinarySensorDeviceClass.LOCK,
    ),
    VsonBinarySensorDeviceClass.MOISTURE: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.MOISTURE,
        device_class=BinarySensorDeviceClass.MOISTURE,
    ),
    VsonBinarySensorDeviceClass.MOTION: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.MOTION,
        device_class=BinarySensorDeviceClass.MOTION,
    ),
    VsonBinarySensorDeviceClass.MOVING: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.MOVING,
        device_class=BinarySensorDeviceClass.MOVING,
    ),
    VsonBinarySensorDeviceClass.OCCUPANCY: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.OCCUPANCY,
        device_class=BinarySensorDeviceClass.OCCUPANCY,
    ),
    VsonBinarySensorDeviceClass.OPENING: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.OPENING,
        device_class=BinarySensorDeviceClass.OPENING,
    ),
    VsonBinarySensorDeviceClass.PLUG: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.PLUG,
        device_class=BinarySensorDeviceClass.PLUG,
    ),
    VsonBinarySensorDeviceClass.POWER: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.POWER,
        device_class=BinarySensorDeviceClass.POWER,
    ),
    VsonBinarySensorDeviceClass.PRESENCE: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.PRESENCE,
        device_class=BinarySensorDeviceClass.PRESENCE,
    ),
    VsonBinarySensorDeviceClass.PROBLEM: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.PROBLEM,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    VsonBinarySensorDeviceClass.RUNNING: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.RUNNING,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    VsonBinarySensorDeviceClass.SAFETY: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.SAFETY,
        device_class=BinarySensorDeviceClass.SAFETY,
    ),
    VsonBinarySensorDeviceClass.SMOKE: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.SMOKE,
        device_class=BinarySensorDeviceClass.SMOKE,
    ),
    VsonBinarySensorDeviceClass.SOUND: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.SOUND,
        device_class=BinarySensorDeviceClass.SOUND,
    ),
    VsonBinarySensorDeviceClass.TAMPER: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.TAMPER,
        device_class=BinarySensorDeviceClass.TAMPER,
    ),
    VsonBinarySensorDeviceClass.VIBRATION: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.VIBRATION,
        device_class=BinarySensorDeviceClass.VIBRATION,
    ),
    VsonBinarySensorDeviceClass.WINDOW: BinarySensorEntityDescription(
        key=VsonBinarySensorDeviceClass.WINDOW,
        device_class=BinarySensorDeviceClass.WINDOW,
    ),
}


def sensor_update_to_bluetooth_data_update(
    sensor_update: SensorUpdate,
) -> PassiveBluetoothDataUpdate[bool | None]:
    """Convert a binary sensor update to a bluetooth data update."""
    return PassiveBluetoothDataUpdate(
        devices={
            device_id: sensor_device_info_to_hass_device_info(device_info)
            for device_id, device_info in sensor_update.devices.items()
        },
        entity_descriptions={
            device_key_to_bluetooth_entity_key(device_key): BINARY_SENSOR_DESCRIPTIONS[
                description.device_class
            ]
            for device_key, description in sensor_update.binary_entity_descriptions.items()
            if description.device_class
        },
        entity_data={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.native_value
            for device_key, sensor_values in sensor_update.binary_entity_values.items()
        },
        entity_names={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.name
            for device_key, sensor_values in sensor_update.binary_entity_values.items()
        },
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VsonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Vson BLE binary sensors."""
    coordinator = entry.runtime_data
    processor = VsonPassiveBluetoothDataProcessor(
        sensor_update_to_bluetooth_data_update
    )
    entry.async_on_unload(
        processor.async_add_entities_listener(
            VsonBluetoothBinarySensorEntity, async_add_entities
        )
    )
    entry.async_on_unload(
        coordinator.async_register_processor(processor, BinarySensorEntityDescription)
    )


class VsonBluetoothBinarySensorEntity(
    PassiveBluetoothProcessorEntity[VsonPassiveBluetoothDataProcessor[bool | None]],
    BinarySensorEntity,
):
    """Representation of a Vson binary sensor."""

    @property
    def is_on(self) -> bool | None:
        """Return the native value."""
        return self.processor.entity_data.get(self.entity_key)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available
