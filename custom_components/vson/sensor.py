"""Support for Vson sensors."""

from __future__ import annotations

from typing import cast
from functools import partial
from .vson_ble import SensorDeviceClass as VsonSensorDeviceClass, SensorUpdate, Units

from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataUpdate,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    ATTR_SW_VERSION,
    ATTR_HW_VERSION,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    EntityCategory,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.sensor import sensor_device_info_to_hass_device_info
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN
from .coordinator import VsonPassiveBluetoothDataProcessor
from .device import device_key_to_bluetooth_entity_key
from .entity import vson_device_info
from .types import VsonConfigEntry

SENSOR_DESCRIPTIONS = {
    # CO2 (parts per million)
    (
        VsonSensorDeviceClass.CO2,
        Units.CONCENTRATION_PARTS_PER_MILLION,
    ): SensorEntityDescription(
        key=f"{VsonSensorDeviceClass.CO2}_{Units.CONCENTRATION_PARTS_PER_MILLION}",
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Temperature (°C)
    (VsonSensorDeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): SensorEntityDescription(
        key=f"{VsonSensorDeviceClass.TEMPERATURE}_{Units.TEMP_CELSIUS}",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Volatile organic Compounds (VOC) (µg/m3)
    (
        VsonSensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
        Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    ): SensorEntityDescription(
        key=f"{VsonSensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS}_{Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER}",
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # HCHO (µg/m3)
    (
        VsonSensorDeviceClass.FORMALDEHYDE,
        Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    ): SensorEntityDescription(
        key=f"{VsonSensorDeviceClass.FORMALDEHYDE}_{Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER}",
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
}

def hass_device_info(sensor_device_info):
    device_info = sensor_device_info_to_hass_device_info(sensor_device_info)
    if sensor_device_info.sw_version is not None:
        device_info[ATTR_SW_VERSION] = sensor_device_info.sw_version
    if sensor_device_info.hw_version is not None:
        device_info[ATTR_HW_VERSION] = sensor_device_info.hw_version
    return device_info

def sensor_update_to_bluetooth_data_update(
    sensor_update: SensorUpdate,
) -> PassiveBluetoothDataUpdate[float | None]:
    """Convert a sensor update to a bluetooth data update."""
    entity_descriptions: dict = {}
    for device_key, description in sensor_update.entity_descriptions.items():
        if not description.device_class:
            continue
        desc_key = (description.device_class, description.native_unit_of_measurement)
        ha_description = SENSOR_DESCRIPTIONS.get(desc_key)
        if ha_description is None:
            continue
        entity_descriptions[device_key_to_bluetooth_entity_key(device_key)] = (
            ha_description
        )

    return PassiveBluetoothDataUpdate(
        devices={
            device_id: hass_device_info(device_info)
            for device_id, device_info in sensor_update.devices.items()
        },
        entity_descriptions=entity_descriptions,
        entity_data={
            device_key_to_bluetooth_entity_key(device_key): cast(
                float | None, sensor_values.native_value
            )
            for device_key, sensor_values in sensor_update.entity_values.items()
            if device_key_to_bluetooth_entity_key(device_key) in entity_descriptions
        },
        entity_names={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.name
            for device_key, sensor_values in sensor_update.entity_values.items()
            if device_key_to_bluetooth_entity_key(device_key) in entity_descriptions
        },
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VsonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Vson BLE sensors."""
    coordinator = entry.runtime_data
    processor = VsonPassiveBluetoothDataProcessor(
        sensor_update_to_bluetooth_data_update
    )
    entry.async_on_unload(
        processor.async_add_entities_listener(
            VsonBluetoothSensorEntity, async_add_entities
        )
    )
    entry.async_on_unload(
        coordinator.async_register_processor(processor, SensorEntityDescription)
    )

    duration_coordinator = hass.data[DOMAIN][entry.entry_id].get("duration_coordinator")
    if duration_coordinator is not None:
        address = hass.data[DOMAIN][entry.entry_id]["address"]
        async_add_entities([VsonPollDurationSensorEntity(address, duration_coordinator)])


class VsonBluetoothSensorEntity(
    PassiveBluetoothProcessorEntity[VsonPassiveBluetoothDataProcessor[float | None]],
    SensorEntity,
):
    """Representation of a Vson BLE sensor."""

    @property
    def native_value(self) -> int | float | None:
        """Return the native value."""
        return self.processor.entity_data.get(self.entity_key)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        poll_coordinator = self.processor.coordinator.poll_coordinator
        remove = poll_coordinator.async_add_listener(partial(self.processor.async_handle_update, poll_coordinator.data))
        self.async_on_remove(remove)


class VsonPollDurationSensorEntity(
    CoordinatorEntity[DataUpdateCoordinator[float | None]],
    SensorEntity,
):
    """Diagnostic sensor for the latest poll duration."""

    _attr_has_entity_name = True
    _attr_translation_key = "poll_duration"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:timer-outline"

    def __init__(
        self,
        address: str,
        coordinator: DataUpdateCoordinator[float | None],
    ) -> None:
        super().__init__(coordinator)
        self._address = address
        self._attr_unique_id = f"{address}_poll_duration"
        self._attr_device_info = vson_device_info(address)

    @property
    def native_value(self) -> float | None:
        """Return wall-clock seconds for the last poll attempt."""
        return self.coordinator.data
