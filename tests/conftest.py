"""Pytest configuration and Home Assistant module mocks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import sys
from typing import Any
from unittest.mock import MagicMock


class MockBase:
    """Base class supporting subscripting for generics in tests."""

    def __init__(self, *args, **kwargs):
        pass

    def __class_getitem__(cls, item):
        return cls


# Mock Home Assistant exceptions
class MockHomeAssistantError(Exception):
    """Mock HomeAssistantError."""


ha_exceptions = MagicMock()
ha_exceptions.HomeAssistantError = MockHomeAssistantError
sys.modules["homeassistant.exceptions"] = ha_exceptions

# Mock voluptuous if not present
if "voluptuous" not in sys.modules:
    sys.modules["voluptuous"] = MagicMock()

# Mock Home Assistant core and submodules
sys.modules["homeassistant"] = MagicMock()
sys.modules["homeassistant.components"] = MagicMock()
sys.modules["homeassistant.components.bluetooth"] = MagicMock()


class MockPassiveCoordinator(MockBase):
    pass


class MockPassiveDataProcessor(MockBase):
    pass


class MockPassiveProcessorEntity(MockBase):
    pass


ha_bt_processor = MagicMock()
ha_bt_processor.PassiveBluetoothProcessorCoordinator = MockPassiveCoordinator
ha_bt_processor.PassiveBluetoothProcessorEntity = MockPassiveProcessorEntity
ha_bt_processor.PassiveBluetoothDataProcessor = MockPassiveDataProcessor


@dataclass
class MockPassiveBluetoothDataUpdate:
    devices: dict = None
    entity_descriptions: dict = None
    entity_data: dict = None
    entity_names: dict = None

    def __post_init__(self):
        if self.devices is None:
            self.devices = {}
        if self.entity_descriptions is None:
            self.entity_descriptions = {}
        if self.entity_data is None:
            self.entity_data = {}
        if self.entity_names is None:
            self.entity_names = {}


ha_bt_processor.PassiveBluetoothDataUpdate = MockPassiveBluetoothDataUpdate
sys.modules["homeassistant.components.bluetooth.passive_update_processor"] = (
    ha_bt_processor
)


class MockSensorEntity(MockBase):
    pass


class MockBinarySensorEntity(MockBase):
    pass


class MockCoordinatorEntity(MockBase):
    def __init__(self, coordinator=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coordinator = coordinator

    @property
    def available(self) -> bool:
        coord = getattr(self, "coordinator", None)
        if coord is not None and hasattr(coord, "last_update_success"):
            return bool(coord.last_update_success)
        return True


class MockDataUpdateCoordinator(MockBase):
    def __init__(self, *args, update_interval=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_interval = update_interval


class SensorDeviceClass(StrEnum):
    CO2 = "carbon_dioxide"
    TEMPERATURE = "temperature"
    VOLATILE_ORGANIC_COMPOUNDS = "volatile_organic_compounds"
    DURATION = "duration"


class SensorStateClass(StrEnum):
    MEASUREMENT = "measurement"
    TOTAL = "total"
    TOTAL_INCREASING = "total_increasing"


@dataclass(frozen=True, kw_only=True)
class SensorEntityDescription:
    key: str
    device_class: SensorDeviceClass | None = None
    native_unit_of_measurement: str | None = None
    state_class: SensorStateClass | None = None
    entity_category: Any | None = None
    icon: str | None = None
    translation_key: str | None = None


ha_sensor = MagicMock()
ha_sensor.SensorEntity = MockSensorEntity
ha_sensor.SensorDeviceClass = SensorDeviceClass
ha_sensor.SensorStateClass = SensorStateClass
ha_sensor.SensorEntityDescription = SensorEntityDescription
sys.modules["homeassistant.components.sensor"] = ha_sensor


class BinarySensorDeviceClass(StrEnum):
    CONNECTIVITY = "connectivity"
    PROBLEM = "problem"


@dataclass(frozen=True, kw_only=True)
class BinarySensorEntityDescription:
    key: str
    device_class: BinarySensorDeviceClass | None = None
    entity_category: Any | None = None


ha_binary_sensor = MagicMock()
ha_binary_sensor.BinarySensorEntity = MockBinarySensorEntity
ha_binary_sensor.BinarySensorDeviceClass = BinarySensorDeviceClass
ha_binary_sensor.BinarySensorEntityDescription = BinarySensorEntityDescription
sys.modules["homeassistant.components.binary_sensor"] = ha_binary_sensor


class Platform(StrEnum):
    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"


class UnitOfDensity(StrEnum):
    MICROGRAMS_PER_CUBIC_METER = "μg/m³"


class UnitOfRatio(StrEnum):
    PARTS_PER_MILLION = "ppm"


class UnitOfTemperature(StrEnum):
    CELSIUS = "°C"


class UnitOfTime(StrEnum):
    SECONDS = "s"


class EntityCategory(StrEnum):
    DIAGNOSTIC = "diagnostic"
    CONFIG = "config"


ha_const = MagicMock()
ha_const.Platform = Platform
ha_const.ATTR_SW_VERSION = "sw_version"
ha_const.ATTR_HW_VERSION = "hw_version"
ha_const.CONF_ADDRESS = "address"
ha_const.EntityCategory = EntityCategory
ha_const.UnitOfDensity = UnitOfDensity
ha_const.UnitOfRatio = UnitOfRatio
ha_const.UnitOfTemperature = UnitOfTemperature
ha_const.UnitOfTime = UnitOfTime
sys.modules["homeassistant.const"] = ha_const

ha_core = MagicMock()
ha_core.HomeAssistant = MagicMock
ha_core.callback = lambda f: f
sys.modules["homeassistant.core"] = ha_core

sys.modules["homeassistant.config_entries"] = MagicMock()
sys.modules["homeassistant.helpers"] = MagicMock()
sys.modules["homeassistant.helpers.device_registry"] = MagicMock()
sys.modules["homeassistant.helpers.entity_platform"] = MagicMock()
sys.modules["homeassistant.helpers.sensor"] = MagicMock()
sys.modules["homeassistant.helpers.sensor"].sensor_device_info_to_hass_device_info = (
    lambda info: {}
)

ha_update_coord = MagicMock()
ha_update_coord.CoordinatorEntity = MockCoordinatorEntity
ha_update_coord.DataUpdateCoordinator = MockDataUpdateCoordinator
sys.modules["homeassistant.helpers.update_coordinator"] = ha_update_coord
