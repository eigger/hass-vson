"""Tests for vson BLE parser."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from home_assistant_bluetooth import BluetoothServiceInfoBleak
from sensor_state_data import Units

from custom_components.vson.vson_ble.const import SERVICE_WP6003
from custom_components.vson.vson_ble.parser import (
    HCHO__CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    TVOC__CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    VsonBluetoothDeviceData,
)


def _make_service_info(
    name: str = "6003#ABCD",
    address: str = "AA:BB:CC:DD:EE:FF",
    service_uuids: list[str] | None = None,
) -> BluetoothServiceInfoBleak:
    """Helper to create a BluetoothServiceInfoBleak instance."""
    uuids = service_uuids if service_uuids is not None else [SERVICE_WP6003]
    device = BLEDevice(address, name, details={})
    adv = AdvertisementData(
        local_name=name,
        manufacturer_data={},
        service_data={},
        service_uuids=uuids,
        rssi=-60,
        tx_power=0,
        platform_data=(),
    )
    return BluetoothServiceInfoBleak.from_device_and_advertisement_data(
        device, adv, "local", 0.0, True
    )


def test_supported():
    """Test device supported check."""
    parser = VsonBluetoothDeviceData()

    # Supported device
    valid_info = _make_service_info("6003#1234", service_uuids=[SERVICE_WP6003])
    assert parser.supported(valid_info) is True

    # Wrong name prefix
    wrong_name_info = _make_service_info("OTHER#1234", service_uuids=[SERVICE_WP6003])
    assert parser.supported(wrong_name_info) is False

    # Missing service UUID
    wrong_uuid_info = _make_service_info("6003#1234", service_uuids=["00001800-0000-1000-8000-00805f9b34fb"])
    assert parser.supported(wrong_uuid_info) is False

    # Empty name
    empty_name_info = _make_service_info("", service_uuids=[SERVICE_WP6003])
    assert parser.supported(empty_name_info) is False


def test_parse_wp6003():
    """Test metadata parsing for WP6003."""
    parser = VsonBluetoothDeviceData()
    info = _make_service_info(name="6003#EEFF", address="AA:BB:CC:DD:EE:FF")

    parser._start_update(info)

    assert parser.title == "WP6003 EEFF"
    assert parser.get_device_name() == "WP6003 EEFF"
    dev_info = parser._get_device_info(None)
    assert dev_info.name == "WP6003 EEFF"
    assert dev_info.model == "Air Quality Monitor"
    assert dev_info.manufacturer == "Vson Technology CO., LTD"


@pytest.mark.asyncio
async def test_async_poll():
    """Test async_poll parsing sensor data."""
    parser = VsonBluetoothDeviceData()
    ble_device = MagicMock()

    # 18-byte sample packet:
    # byte 6-7: temp (0x0109 = 265 -> 26.5 °C)
    # byte 10-11: tvoc (0x0065 = 101 -> 0.101 -> 0.1 μg/m³)
    # byte 12-13: hcho (0x000F = 15 -> 0.015 -> 0.01 μg/m³)
    # byte 16-17: co2 (0x0251 = 593 ppm)
    raw_data = bytes.fromhex("0a0001010e02010908000065000f01000251")

    with patch(
        "custom_components.vson.vson_ble.parser.get_sensor_data",
        new=AsyncMock(return_value=raw_data),
    ):
        update = await parser.async_poll(ble_device)

    assert update is not None
    # Verify predefined sensor descriptions
    assert TVOC__CONCENTRATION_MICROGRAMS_PER_CUBIC_METER.native_unit_of_measurement == Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
    assert HCHO__CONCENTRATION_MICROGRAMS_PER_CUBIC_METER.native_unit_of_measurement == Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
