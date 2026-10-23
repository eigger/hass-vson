"""Exercise actual HA setup, platforms, failure recovery and connection cleanup."""

import asyncio
from unittest.mock import patch

from blesession import Unreachable
from blesession.testing import FakeDevice
from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import entity_registry as er
import pytest

from .conftest import ADDRESS, PACKET

pytestmark = pytest.mark.usefixtures("mock_bluetooth")


def entity_state(hass, key):
    registry = er.async_get(hass)
    domain = "binary_sensor" if key in ("connection", "problem") else "sensor"
    entity_id = registry.async_get_entity_id(domain, "vson", f"{ADDRESS}_{key}")
    assert entity_id is not None, key
    state = hass.states.get(entity_id)
    assert state is not None
    return state


async def setup_entry(hass, entry):
    with patch(
        "custom_components.vson.ble_session.ble_device_or_raise",
        return_value=FakeDevice(),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()


async def test_setup_and_unload(hass, mock_config_entry, mock_client):
    await setup_entry(hass, mock_config_entry)
    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert entity_state(hass, "connection").state == "off"
    assert entity_state(hass, "problem").state == "off"
    assert entity_state(hass, "error_count").state == "0"
    assert entity_state(hass, "last_error").state == "unknown"
    assert float(entity_state(hass, "poll_duration").state) >= 0
    assert entity_state(hass, "problem").attributes["success"] is True
    states = hass.states.async_all("sensor")
    assert any(s.state == "593" for s in states)
    assert any(s.state == "26.5" for s in states)
    registry = er.async_get(hass)
    entries = er.async_entries_for_config_entry(registry, mock_config_entry.entry_id)
    assert len({e.device_id for e in entries}) == 1
    assert len(entries) == 10  # four measurements and six diagnostic entities
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_client.disconnects == 1
    assert not mock_client.subscribed
    assert mock_config_entry.entry_id not in hass.data["vson"]


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


async def test_initial_failure_does_not_block_setup(
    hass, mock_config_entry, mock_client
):
    with patch(
        "custom_components.vson.ble_session.ble_device_or_raise",
        side_effect=Unreachable(ADDRESS),
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert entity_state(hass, "problem").state == "on"
    assert entity_state(hass, "connection").state == "off"
    assert mock_client.disconnects == 0


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


async def test_invalid_packet_reports_transfer_failure(
    hass, mock_config_entry, mock_client
):
    mock_client.on_write = lambda _char, _data: mock_client.reply(PACKET[:4])
    await setup_entry(hass, mock_config_entry)
    report = entity_state(hass, "problem").attributes
    assert report["failed_stage"] == "transfer"
    assert report["failed_detail"] == "readout"
    assert "invalid measurement" in report["likely_cause"]


async def test_options_reload_updates_interval(hass, mock_config_entry, mock_client):
    from datetime import timedelta

    await setup_entry(hass, mock_config_entry)
    old_session = hass.data["vson"][mock_config_entry.entry_id]["session"]
    mock_client.is_connected = True
    with patch(
        "custom_components.vson.ble_session.ble_device_or_raise",
        return_value=FakeDevice(),
    ):
        result = await hass.config_entries.options.async_init(
            mock_config_entry.entry_id
        )
        await hass.config_entries.options.async_configure(
            result["flow_id"], user_input={"scan_interval": 60}
        )
        await hass.async_block_till_done()
    assert mock_config_entry.runtime_data.poll_coordinator.update_interval == timedelta(
        seconds=60
    )
    assert hass.data["vson"][mock_config_entry.entry_id]["session"] is not old_session
    assert entity_state(hass, "problem").state == "off"
