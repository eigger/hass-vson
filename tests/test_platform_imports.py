"""Tests for platform imports in vson."""

from __future__ import annotations

import importlib


def test_import_all_platforms():
    """Verify that all platform modules and components can be imported without errors."""
    modules = [
        "custom_components.vson",
        "custom_components.vson.const",
        "custom_components.vson.types",
        "custom_components.vson.device",
        "custom_components.vson.entity",
        "custom_components.vson.coordinator",
        "custom_components.vson.config_flow",
        "custom_components.vson.sensor",
        "custom_components.vson.binary_sensor",
        "custom_components.vson.ble_session",
        "custom_components.vson.vson_ble",
        "custom_components.vson.vson_ble.const",
        "custom_components.vson.vson_ble.parser",
        "custom_components.vson.vson_ble.writer",
    ]

    for mod in modules:
        m = importlib.import_module(mod)
        assert m is not None
