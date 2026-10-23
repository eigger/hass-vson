"""Polling policy is bounded, serialized, and does not count cancellations."""

import asyncio
from unittest.mock import MagicMock, patch

from blesession import SessionReports
from blesession.testing import FakeDevice
from homeassistant.helpers.update_coordinator import UpdateFailed
import pytest

from custom_components.vson.ble_session import VsonBleSession
from custom_components.vson.vson_ble import VsonBluetoothDeviceData


def make_session(hass):
    entry_data = {
        key: MagicMock()
        for key in (
            "connection_coordinator",
            "duration_coordinator",
            "reports_coordinator",
        )
    }
    return VsonBleSession(
        hass, "AA:BB:CC:DD:EE:FF", VsonBluetoothDeviceData(), entry_data
    )


async def test_cancellation_is_not_a_failure(hass, mock_client):
    session = make_session(hass)
    started = asyncio.Event()
    mock_client.on_write = lambda _char, _data: started.set()
    with patch(
        "custom_components.vson.ble_session.ble_device_or_raise",
        return_value=FakeDevice(),
    ):
        task = asyncio.create_task(session.async_poll())
        await started.wait()
        await session.async_shutdown()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert session.reports.failures == 0
    assert session.reports.last is None
    assert not session.lock.locked()
    assert mock_client.disconnects == 1


async def test_attempt_timeout_records_failure(hass, mock_client):
    session = make_session(hass)
    mock_client.on_write = None
    with (
        patch(
            "custom_components.vson.ble_session.ble_device_or_raise",
            return_value=FakeDevice(),
        ),
        patch("custom_components.vson.ble_session.POLL_TIMEOUT_S", 0.01),
    ):
        with pytest.raises(UpdateFailed):
            await session.async_poll()
    assert session.reports.failures == 1
    assert session.reports.last["timed_out"] is True
    assert not session.lock.locked()
    assert mock_client.disconnects == 1


async def test_diagnostic_report_failure_does_not_lose_measurement(hass, mock_client):
    session = make_session(hass)
    with (
        patch(
            "custom_components.vson.ble_session.ble_device_or_raise",
            return_value=FakeDevice(),
        ),
        patch(
            "custom_components.vson.ble_session.report_attempt",
            side_effect=ValueError("diagnostics failed"),
        ),
    ):
        update = await session.async_poll()
    assert update.entity_values
    assert isinstance(session.reports, SessionReports)
    assert session.reports.last["success"] is True
