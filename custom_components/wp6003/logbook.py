"""Describe wp6003 logbook events."""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.components.logbook import LOGBOOK_ENTRY_MESSAGE, LOGBOOK_ENTRY_NAME
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr

from .const import WP6003_BLE_EVENT, DOMAIN, Wp6003BleEvent


@callback
def async_describe_events(
    hass: HomeAssistant,
    async_describe_event: Callable[
        [str, str, Callable[[Event[Wp6003BleEvent]], dict[str, str]]], None
    ],
) -> None:
    """Describe logbook events."""
    dev_reg = dr.async_get(hass)

    @callback
    def async_describe_wp6003_event(event: Event[Wp6003BleEvent]) -> dict[str, str]:
        """Describe wp6003 logbook event."""
        data = event.data
        device = dev_reg.async_get(data["device_id"])
        name = (device and device.name) or f"Wp6003 {data['address']}"
        if properties := data["event_properties"]:
            message = f"{data['event_class']} {data['event_type']}: {properties}"
        else:
            message = f"{data['event_class']} {data['event_type']}"
        return {
            LOGBOOK_ENTRY_NAME: name,
            LOGBOOK_ENTRY_MESSAGE: message,
        }

    async_describe_event(DOMAIN, WP6003_BLE_EVENT, async_describe_wp6003_event)
