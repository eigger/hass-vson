"""Tests for vson config flow and options flow."""

from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from custom_components.vson.config_flow import (
    VsonConfigFlow,
    VsonOptionsFlowHandler,
)
from custom_components.vson.const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)


def test_async_get_options_flow():
    """Test getting options flow handler from config flow."""
    config_entry = MagicMock()
    config_entry.options = {}

    options_flow = VsonConfigFlow.async_get_options_flow(config_entry)
    assert isinstance(options_flow, VsonOptionsFlowHandler)
    assert options_flow.config_entry == config_entry


@pytest.mark.asyncio
async def test_options_flow_init_form():
    """Test options flow displays init form with default scan interval."""
    config_entry = MagicMock()
    config_entry.options = {}

    handler = VsonOptionsFlowHandler(config_entry)
    handler.async_show_form = MagicMock(return_value={"type": "form", "step_id": "init"})

    result = await handler.async_step_init()
    assert result["type"] == "form"
    assert result["step_id"] == "init"
    handler.async_show_form.assert_called_once()


@pytest.mark.asyncio
async def test_options_flow_init_save():
    """Test options flow saves updated scan interval."""
    config_entry = MagicMock()
    config_entry.options = {CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL}

    handler = VsonOptionsFlowHandler(config_entry)
    handler.async_create_entry = MagicMock(
        side_effect=lambda title, data: {"type": "create_entry", "title": title, "data": data}
    )

    result = await handler.async_step_init({CONF_SCAN_INTERVAL: 60})
    assert result["type"] == "create_entry"
    assert result["data"] == {CONF_SCAN_INTERVAL: 60}
    handler.async_create_entry.assert_called_once_with(title="", data={CONF_SCAN_INTERVAL: 60})
