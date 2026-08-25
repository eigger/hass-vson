"""Tests for vson BLE writer/client."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.vson.vson_ble.writer import (
    CHAR_CMD,
    CHAR_NOTI,
    VsonClient,
    get_sensor_data,
)


@pytest.mark.asyncio
async def test_vson_client_request_data():
    """Test VsonClient request_data flow."""
    bleak_client = MagicMock()
    bleak_client.start_notify = AsyncMock()
    bleak_client.stop_notify = AsyncMock()
    bleak_client.write_gatt_char = AsyncMock()

    client = VsonClient(bleak_client)

    # Simulate notification arriving after write
    async def fake_write(uuid, data):
        client._notification_handler(None, bytearray(b"\x01\x02\x03\x04"))

    bleak_client.write_gatt_char.side_effect = fake_write

    with patch("custom_components.vson.vson_ble.writer.sleep", new=AsyncMock()):
        result = await client.request_data()

    bleak_client.start_notify.assert_called_once()
    assert bleak_client.start_notify.call_args[0][0] == CHAR_NOTI
    bleak_client.write_gatt_char.assert_called_once_with(CHAR_CMD, bytes([0xAB]))
    bleak_client.stop_notify.assert_called_once_with(CHAR_NOTI)
    assert result == b"\x01\x02\x03\x04"


@pytest.mark.asyncio
async def test_get_sensor_data_success():
    """Test get_sensor_data helper."""
    ble_device = MagicMock()
    ble_device.address = "AA:BB:CC:DD:EE:FF"

    mock_client = MagicMock()
    mock_client.is_connected = True
    mock_client.services = []
    mock_client.disconnect = AsyncMock()

    with patch(
        "custom_components.vson.vson_ble.writer.establish_connection",
        new=AsyncMock(return_value=mock_client),
    ), patch(
        "custom_components.vson.vson_ble.writer.VsonClient.request_data",
        new=AsyncMock(return_value=b"\x01\x02\x03"),
    ):
        data = await get_sensor_data(ble_device)

    assert data == b"\x01\x02\x03"
    mock_client.disconnect.assert_called_once()
