"""Constants for the Wp6003 Bluetooth integration."""

from __future__ import annotations

from typing import Final, TypedDict

DOMAIN = "wp6003"
LOCK = "lock"
CONF_BINDKEY: Final = "bindkey"
CONF_DISCOVERED_EVENT_CLASSES: Final = "known_events"
CONF_SUBTYPE: Final = "subtype"

EVENT_TYPE: Final = "event_type"
EVENT_CLASS: Final = "event_class"
EVENT_PROPERTIES: Final = "event_properties"
WP6003_BLE_EVENT: Final = "wp6003_ble_event"


EVENT_CLASS_BUTTON: Final = "button"
EVENT_CLASS_DIMMER: Final = "dimmer"

CONF_EVENT_CLASS: Final = "event_class"
CONF_EVENT_PROPERTIES: Final = "event_properties"


class Wp6003BleEvent(TypedDict):
    """Wp6003 BLE event data."""

    device_id: str
    address: str
    event_class: str  # ie 'button'
    event_type: str  # ie 'press'
    event_properties: dict[str, str | int | float | None] | None
