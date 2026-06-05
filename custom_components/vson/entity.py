"""Shared helpers for Vson diagnostic entities."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo

MODEL = "WP6003"
MANUFACTURER = "Vson Technology CO., LTD"


def vson_device_info(address: str) -> DeviceInfo:
    """Build DeviceInfo matching the passive Bluetooth device for this address."""
    identifier = address.replace(":", "")[-4:]
    return DeviceInfo(
        connections={(CONNECTION_BLUETOOTH, address)},
        manufacturer=MANUFACTURER,
        model=MODEL,
        name=f"{MODEL} {identifier}",
    )
