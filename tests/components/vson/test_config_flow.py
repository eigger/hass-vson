"""Config and options flows through the real HA flow manager."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
import pytest

from custom_components.vson.const import CONF_SCAN_INTERVAL
from .test_parser import _make_service_info

pytestmark = pytest.mark.usefixtures("mock_bluetooth")


async def test_options_form_and_save(hass, mock_config_entry):
    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={CONF_SCAN_INTERVAL: 60}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_SCAN_INTERVAL: 60}
    assert mock_config_entry.options[CONF_SCAN_INTERVAL] == 60


async def test_options_reject_invalid_interval(hass, mock_config_entry):
    import voluptuous as vol

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    for value in (29, 86401):
        with pytest.raises(vol.Invalid):
            result["data_schema"]({CONF_SCAN_INTERVAL: value})


async def test_no_devices(hass):
    with patch(
        "custom_components.vson.config_flow.async_discovered_service_info",
        return_value=[],
    ):
        result = await hass.config_entries.flow.async_init(
            "vson", context={"source": config_entries.SOURCE_USER}
        )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_devices_found"


async def test_duplicate_bluetooth_discovery(hass, mock_config_entry):
    result = await hass.config_entries.flow.async_init(
        "vson",
        context={"source": config_entries.SOURCE_BLUETOOTH},
        data=_make_service_info(),
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_unsupported_bluetooth_discovery(hass):
    result = await hass.config_entries.flow.async_init(
        "vson",
        context={"source": config_entries.SOURCE_BLUETOOTH},
        data=_make_service_info(name="OTHER#1234"),
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "not_supported"


async def test_user_flow_creates_and_loads_entry(hass, mock_client):
    from blesession.testing import FakeDevice

    with (
        patch(
            "custom_components.vson.config_flow.async_discovered_service_info",
            return_value=[_make_service_info()],
        ),
        patch(
            "custom_components.vson.ble_session.ble_device_or_raise",
            return_value=FakeDevice(),
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            "vson", context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] is FlowResultType.FORM
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={"address": "AA:BB:CC:DD:EE:FF"}
        )
        await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].unique_id == "AA:BB:CC:DD:EE:FF"
    assert result["result"].runtime_data.poll_coordinator.last_update_success
