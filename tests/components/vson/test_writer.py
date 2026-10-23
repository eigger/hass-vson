"""WP6003 protocol over the real shared BLE transport with its official fake."""

import asyncio

from bleak.exc import BleakError
from blesession import (
    ConnectFailed,
    GattMismatch,
    NotificationTimeout,
    SessionDropped,
    SessionTrace,
)
from blesession.testing import FakeDevice, fake_connect
import pytest

from custom_components.vson.vson_ble.writer import (
    CHAR_CMD,
    InvalidSensorResponse,
    get_sensor_data,
)
from .conftest import PACKET


async def test_get_sensor_data_success(mock_client):
    states = []
    result = await get_sensor_data(FakeDevice(), on_connection=states.append)
    assert result == PACKET
    assert mock_client.writes == [(CHAR_CMD, b"\xab", None)]
    assert mock_client.disconnects == 1
    assert not mock_client.subscribed
    assert states[0] is True
    assert states[-1] is False


async def test_connect_failure(monkeypatch):
    monkeypatch.setattr(
        "blesession.session.establish_connection",
        fake_connect(fail=BleakError("no slot")),
    )
    states = []
    with pytest.raises(ConnectFailed):
        await get_sensor_data(FakeDevice(), on_connection=states.append)
    assert True not in states


async def test_missing_gatt(mock_client):
    mock_client.services.by_uuid.clear()
    with pytest.raises(GattMismatch):
        await get_sensor_data(FakeDevice())
    assert mock_client.disconnects == 1


async def test_invalid_reply(mock_client):
    mock_client.on_write = lambda _char, _data: mock_client.reply(b"bad")
    with pytest.raises(InvalidSensorResponse):
        await get_sensor_data(FakeDevice())
    assert mock_client.disconnects == 1


async def test_timeout(mock_client, monkeypatch):
    mock_client.on_write = None
    monkeypatch.setattr("custom_components.vson.vson_ble.writer.REPLY_TIMEOUT_S", 0.01)
    with pytest.raises(NotificationTimeout):
        await get_sensor_data(FakeDevice())
    assert mock_client.disconnects == 1
    assert not mock_client.subscribed


async def test_disconnect_while_waiting(mock_client):
    mock_client.on_write = lambda _char, _data: mock_client.drop()
    with pytest.raises(SessionDropped):
        await get_sensor_data(FakeDevice())


async def test_cancel_cleans_up(mock_client):
    started = asyncio.Event()
    mock_client.on_write = lambda _char, _data: started.set()
    task = asyncio.create_task(get_sensor_data(FakeDevice()))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert mock_client.disconnects == 1
    assert not mock_client.subscribed


async def test_disconnect_failure_preserves_valid_result(mock_client):
    mock_client.fail_disconnect = BleakError("close failed")
    trace = SessionTrace()
    assert await get_sensor_data(FakeDevice(), trace=trace) == PACKET
    assert "disconnect_error" in trace.facts


async def test_write_with_response_profile_preserves_bleak_selection(mock_client):
    from custom_components.vson.vson_ble.const import SERVICE_WP6003

    mock_client.add_characteristic(SERVICE_WP6003, CHAR_CMD, properties=("write",))
    assert await get_sensor_data(FakeDevice()) == PACKET
    assert mock_client.writes == [(CHAR_CMD, b"\xab", None)]
