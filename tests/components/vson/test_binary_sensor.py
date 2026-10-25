"""Exercise connection and communication-problem entities in real HA."""

import asyncio
from unittest.mock import patch

import pytest
from blesession import Unreachable
from blesession.testing import FakeDevice

from .conftest import ADDRESS
from .test_init import entity_state, setup_entry

pytestmark = pytest.mark.usefixtures("mock_bluetooth")


async def test_failure_and_recovery(hass, mock_config_entry, mock_client):
    await setup_entry(hass, mock_config_entry)
    poll = mock_config_entry.runtime_data.poll_coordinator
    with patch(
        "custom_components.vson.ble_session.ble_device_or_raise",
        side_effect=Unreachable(ADDRESS),
    ):
        await poll.async_refresh()
    await hass.async_block_till_done()
    assert entity_state(hass, "problem").state == "on"
    assert entity_state(hass, "error_count").state == "1"
    assert entity_state(hass, "problem").attributes["failed_stage"] == "unreachable"
    last_error = entity_state(hass, "last_error").state
    last_failure = entity_state(hass, "last_failure").state
    assert last_failure not in ("unknown", "unavailable")
    assert any(s.state == "unavailable" for s in hass.states.async_all("sensor"))
    mock_client.is_connected = True
    with patch(
        "custom_components.vson.ble_session.ble_device_or_raise",
        return_value=FakeDevice(),
    ):
        await poll.async_refresh()
    await hass.async_block_till_done()
    assert entity_state(hass, "problem").state == "off"
    assert entity_state(hass, "error_count").state == "1"
    assert entity_state(hass, "last_error").state == last_error
    assert entity_state(hass, "last_failure").state == last_failure
    assert any(s.state == "593" for s in hass.states.async_all("sensor"))


async def test_unload_cancels_active_poll(hass, mock_config_entry, mock_client):
    await setup_entry(hass, mock_config_entry)
    mock_client.is_connected = True
    started = asyncio.Event()
    mock_client.on_write = lambda _char, _data: started.set()
    with patch(
        "custom_components.vson.ble_session.ble_device_or_raise",
        return_value=FakeDevice(),
    ):
        task = asyncio.create_task(
            mock_config_entry.runtime_data.poll_coordinator.async_refresh()
        )
        await started.wait()
        await hass.async_block_till_done(wait_background_tasks=False)
        assert entity_state(hass, "connection").state == "on"
        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
        with pytest.raises(asyncio.CancelledError):
            await task
    assert mock_client.disconnects == 2
    assert not mock_client.subscribed
