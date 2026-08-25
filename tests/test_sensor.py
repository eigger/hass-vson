"""Tests for vson sensor platform."""

from __future__ import annotations

from unittest.mock import MagicMock
from homeassistant.const import (
    UnitOfDensity,
    UnitOfRatio,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from custom_components.vson.vson_ble import SensorDeviceClass as VsonSensorDeviceClass, Units
from custom_components.vson.sensor import (
    SENSOR_DESCRIPTIONS,
    VsonPollDurationSensorEntity,
    sensor_update_to_bluetooth_data_update,
)


def test_sensor_descriptions_units():
    """Verify SENSOR_DESCRIPTIONS has correct UnitOfDensity and UnitOfRatio."""
    # CO2
    co2_desc = SENSOR_DESCRIPTIONS[(VsonSensorDeviceClass.CO2, Units.CONCENTRATION_PARTS_PER_MILLION)]
    assert co2_desc.native_unit_of_measurement == UnitOfRatio.PARTS_PER_MILLION
    assert co2_desc.device_class == SensorDeviceClass.CO2
    assert co2_desc.state_class == SensorStateClass.MEASUREMENT

    # Temperature
    temp_desc = SENSOR_DESCRIPTIONS[(VsonSensorDeviceClass.TEMPERATURE, Units.TEMP_CELSIUS)]
    assert temp_desc.native_unit_of_measurement == UnitOfTemperature.CELSIUS
    assert temp_desc.device_class == SensorDeviceClass.TEMPERATURE

    # VOC
    voc_desc = SENSOR_DESCRIPTIONS[(VsonSensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER)]
    assert voc_desc.native_unit_of_measurement == UnitOfDensity.MICROGRAMS_PER_CUBIC_METER
    assert voc_desc.device_class == SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS

    # Formaldehyde (HCHO)
    hcho_desc = SENSOR_DESCRIPTIONS[(VsonSensorDeviceClass.FORMALDEHYDE, Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER)]
    assert hcho_desc.native_unit_of_measurement == UnitOfDensity.MICROGRAMS_PER_CUBIC_METER
    assert hcho_desc.device_class == SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS


def test_poll_duration_sensor_entity():
    """Test diagnostic duration sensor entity."""
    coordinator = MagicMock()
    coordinator.data = 1.23

    entity = VsonPollDurationSensorEntity("AA:BB:CC:DD:EE:FF", coordinator)
    assert entity.native_value == 1.23
    assert entity._attr_native_unit_of_measurement == UnitOfTime.SECONDS
    assert entity._attr_unique_id == "AA:BB:CC:DD:EE:FF_poll_duration"


def test_sensor_update_to_bluetooth_data_update():
    """Test sensor_update_to_bluetooth_data_update mapping."""
    sensor_update = MagicMock()
    sensor_update.devices = {}
    sensor_update.entity_descriptions = {}
    sensor_update.entity_values = {}

    data_update = sensor_update_to_bluetooth_data_update(sensor_update)
    assert data_update is not None
    assert data_update.devices == {}
    assert data_update.entity_descriptions == {}


def test_sensor_update_to_bluetooth_data_update_none():
    """Test sensor_update_to_bluetooth_data_update with None argument."""
    data_update = sensor_update_to_bluetooth_data_update(None)
    assert data_update is not None
    assert data_update.devices == {}
    assert data_update.entity_descriptions == {}

