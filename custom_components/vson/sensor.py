"""Support for Vson sensors."""

from __future__ import annotations

from functools import lru_cache
from blesession import SessionReports
from typing import cast
from .vson_ble import (
    SensorDeviceClass as VsonSensorDeviceClass,
    SensorDeviceInfo,
    SensorUpdate,
    Units,
)

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
    ATTR_HW_VERSION,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_SW_VERSION,
    EntityCategory,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
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
        native_unit_of_measurement="ppm",
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
        native_unit_of_measurement="µg/m³",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # HCHO (µg/m3)
    (
        VsonSensorDeviceClass.FORMALDEHYDE,
        Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    ): SensorEntityDescription(
        key=f"{VsonSensorDeviceClass.FORMALDEHYDE}_{Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER}",
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
        native_unit_of_measurement="µg/m³",
        state_class=SensorStateClass.MEASUREMENT,
    ),
}


def hass_device_info(sensor_device_info: SensorDeviceInfo) -> DeviceInfo:
    """Convert sensor device info, including its firmware and hardware versions."""
    return _hass_device_info(
        sensor_device_info.name,
        sensor_device_info.manufacturer,
        sensor_device_info.model,
        sensor_device_info.sw_version,
        sensor_device_info.hw_version,
    )


@lru_cache(maxsize=64)
def _hass_device_info(
    name: str | None,
    manufacturer: str | None,
    model: str | None,
    sw_version: str | None,
    hw_version: str | None,
) -> DeviceInfo:
    """Return a cached device info for the given values."""
    device_info = DeviceInfo()
    for key, value in (
        (ATTR_NAME, name),
        (ATTR_MANUFACTURER, manufacturer),
        (ATTR_MODEL, model),
        (ATTR_SW_VERSION, sw_version),
        (ATTR_HW_VERSION, hw_version),
    ):
        if value is not None:
            device_info[key] = value
    return device_info


def sensor_update_to_bluetooth_data_update(
    sensor_update: SensorUpdate | None,
) -> PassiveBluetoothDataUpdate[float | None]:
    """Convert a sensor update to a bluetooth data update."""
    if not sensor_update:
        return PassiveBluetoothDataUpdate()

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
        async_add_entities(
            [VsonPollDurationSensorEntity(address, duration_coordinator)]
        )

    reports_coordinator = hass.data[DOMAIN][entry.entry_id]["reports_coordinator"]
    address = hass.data[DOMAIN][entry.entry_id]["address"]
    async_add_entities(
        [
            VsonSessionSensorEntity(address, reports_coordinator, key)
            for key in ("last_error", "error_count", "last_failure")
        ]
    )


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
        return (
            super().available
            and self.processor.coordinator.poll_coordinator.last_update_success
        )


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


class VsonSessionSensorEntity(
    CoordinatorEntity[DataUpdateCoordinator[SessionReports]], SensorEntity
):
    """Shared session reports presented as HA diagnostics."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, address: str, coordinator, key: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_translation_key = key
        self._attr_unique_id = f"{address}_{key}"
        self._attr_device_info = vson_device_info(address)
        if key == "last_failure":
            self._attr_device_class = SensorDeviceClass.TIMESTAMP
        elif key == "error_count":
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            self._attr_icon = "mdi:counter"
        else:
            self._attr_icon = "mdi:alert-circle-outline"

    @property
    def native_value(self):
        """Return retained evidence; success never erases the last failure."""
        reports = self.coordinator.data
        if self._key == "error_count":
            return reports.failures
        if self._key == "last_failure":
            return reports.last_failure_at
        report = reports.last_failure or {}
        error = report.get("error")
        return str(error)[:255] if error is not None else None

    @property
    def extra_state_attributes(self):
        """Expose the standard failure stage, cause, timings and radio facts."""
        return dict(self.coordinator.data.last_failure or {})
