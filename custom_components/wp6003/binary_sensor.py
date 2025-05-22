"""Support for Wp6003 binary sensors."""

from __future__ import annotations

from .wp6003_ble import (
    BinarySensorDeviceClass as Wp6003BinarySensorDeviceClass,
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

from .coordinator import Wp6003PassiveBluetoothDataProcessor
from .device import device_key_to_bluetooth_entity_key
from .types import Wp6003ConfigEntry

BINARY_SENSOR_DESCRIPTIONS = {
    Wp6003BinarySensorDeviceClass.BATTERY: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.BATTERY,
        device_class=BinarySensorDeviceClass.BATTERY,
    ),
    Wp6003BinarySensorDeviceClass.BATTERY_CHARGING: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.BATTERY_CHARGING,
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
    ),
    Wp6003BinarySensorDeviceClass.CO: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.CO,
        device_class=BinarySensorDeviceClass.CO,
    ),
    Wp6003BinarySensorDeviceClass.COLD: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.COLD,
        device_class=BinarySensorDeviceClass.COLD,
    ),
    Wp6003BinarySensorDeviceClass.CONNECTIVITY: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.CONNECTIVITY,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    Wp6003BinarySensorDeviceClass.DOOR: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.DOOR,
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    Wp6003BinarySensorDeviceClass.HEAT: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.HEAT,
        device_class=BinarySensorDeviceClass.HEAT,
    ),
    Wp6003BinarySensorDeviceClass.GARAGE_DOOR: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.GARAGE_DOOR,
        device_class=BinarySensorDeviceClass.GARAGE_DOOR,
    ),
    Wp6003BinarySensorDeviceClass.GAS: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.GAS,
        device_class=BinarySensorDeviceClass.GAS,
    ),
    Wp6003BinarySensorDeviceClass.GENERIC: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.GENERIC,
    ),
    Wp6003BinarySensorDeviceClass.LIGHT: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.LIGHT,
        device_class=BinarySensorDeviceClass.LIGHT,
    ),
    Wp6003BinarySensorDeviceClass.LOCK: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.LOCK,
        device_class=BinarySensorDeviceClass.LOCK,
    ),
    Wp6003BinarySensorDeviceClass.MOISTURE: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.MOISTURE,
        device_class=BinarySensorDeviceClass.MOISTURE,
    ),
    Wp6003BinarySensorDeviceClass.MOTION: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.MOTION,
        device_class=BinarySensorDeviceClass.MOTION,
    ),
    Wp6003BinarySensorDeviceClass.MOVING: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.MOVING,
        device_class=BinarySensorDeviceClass.MOVING,
    ),
    Wp6003BinarySensorDeviceClass.OCCUPANCY: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.OCCUPANCY,
        device_class=BinarySensorDeviceClass.OCCUPANCY,
    ),
    Wp6003BinarySensorDeviceClass.OPENING: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.OPENING,
        device_class=BinarySensorDeviceClass.OPENING,
    ),
    Wp6003BinarySensorDeviceClass.PLUG: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.PLUG,
        device_class=BinarySensorDeviceClass.PLUG,
    ),
    Wp6003BinarySensorDeviceClass.POWER: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.POWER,
        device_class=BinarySensorDeviceClass.POWER,
    ),
    Wp6003BinarySensorDeviceClass.PRESENCE: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.PRESENCE,
        device_class=BinarySensorDeviceClass.PRESENCE,
    ),
    Wp6003BinarySensorDeviceClass.PROBLEM: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.PROBLEM,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    Wp6003BinarySensorDeviceClass.RUNNING: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.RUNNING,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    Wp6003BinarySensorDeviceClass.SAFETY: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.SAFETY,
        device_class=BinarySensorDeviceClass.SAFETY,
    ),
    Wp6003BinarySensorDeviceClass.SMOKE: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.SMOKE,
        device_class=BinarySensorDeviceClass.SMOKE,
    ),
    Wp6003BinarySensorDeviceClass.SOUND: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.SOUND,
        device_class=BinarySensorDeviceClass.SOUND,
    ),
    Wp6003BinarySensorDeviceClass.TAMPER: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.TAMPER,
        device_class=BinarySensorDeviceClass.TAMPER,
    ),
    Wp6003BinarySensorDeviceClass.VIBRATION: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.VIBRATION,
        device_class=BinarySensorDeviceClass.VIBRATION,
    ),
    Wp6003BinarySensorDeviceClass.WINDOW: BinarySensorEntityDescription(
        key=Wp6003BinarySensorDeviceClass.WINDOW,
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
    entry: Wp6003ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Wp6003 BLE binary sensors."""
    coordinator = entry.runtime_data
    processor = Wp6003PassiveBluetoothDataProcessor(
        sensor_update_to_bluetooth_data_update
    )
    entry.async_on_unload(
        processor.async_add_entities_listener(
            Wp6003BluetoothBinarySensorEntity, async_add_entities
        )
    )
    entry.async_on_unload(
        coordinator.async_register_processor(processor, BinarySensorEntityDescription)
    )


class Wp6003BluetoothBinarySensorEntity(
    PassiveBluetoothProcessorEntity[Wp6003PassiveBluetoothDataProcessor[bool | None]],
    BinarySensorEntity,
):
    """Representation of a Wp6003 binary sensor."""

    @property
    def is_on(self) -> bool | None:
        """Return the native value."""
        return self.processor.entity_data.get(self.entity_key)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available
