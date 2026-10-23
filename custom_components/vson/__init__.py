"""The Vson Bluetooth integration."""

from __future__ import annotations

from datetime import timedelta
from functools import partial
import logging

from blesession import SessionReports
from homeassistant.components.bluetooth import (
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .ble_session import VsonBleSession
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import VsonPassiveBluetoothProcessorCoordinator
from .types import VsonConfigEntry
from .vson_ble import SensorUpdate, VsonBluetoothDeviceData

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


def process_service_info(
    entry: VsonConfigEntry,
    service_info: BluetoothServiceInfoBleak,
) -> SensorUpdate:
    """Update device metadata from passive advertisements."""
    return entry.runtime_data.device_data.update(service_info)


async def async_setup_entry(hass: HomeAssistant, entry: VsonConfigEntry) -> bool:
    """Set up Vson Bluetooth from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    address = entry.unique_id
    assert address is not None

    data = VsonBluetoothDeviceData()
    hass.data[DOMAIN][entry.entry_id] = {}
    hass.data[DOMAIN][entry.entry_id]["address"] = address
    hass.data[DOMAIN][entry.entry_id]["data"] = data

    bt_coordinator = VsonPassiveBluetoothProcessorCoordinator(
        hass,
        _LOGGER,
        address=address,
        mode=BluetoothScanningMode.PASSIVE,
        update_method=partial(process_service_info, entry),
        device_data=data,
        connectable=True,
        entry=entry,
    )

    connection_coordinator = DataUpdateCoordinator[bool](
        hass,
        _LOGGER,
        name=f"{DOMAIN}_connection_{address}",
    )
    duration_coordinator = DataUpdateCoordinator[float | None](
        hass,
        _LOGGER,
        name=f"{DOMAIN}_duration_{address}",
    )
    connection_coordinator.async_set_updated_data(False)
    duration_coordinator.async_set_updated_data(None)
    hass.data[DOMAIN][entry.entry_id]["connection_coordinator"] = connection_coordinator
    hass.data[DOMAIN][entry.entry_id]["duration_coordinator"] = duration_coordinator

    reports_coordinator = DataUpdateCoordinator[SessionReports](
        hass,
        _LOGGER,
        name=f"{DOMAIN}_reports_{address}",
    )
    entry_data = hass.data[DOMAIN][entry.entry_id]
    entry_data["reports_coordinator"] = reports_coordinator
    session = VsonBleSession(hass, address, data, entry_data)
    reports_coordinator.async_set_updated_data(session.reports)
    entry_data["session"] = session
    entry.async_on_unload(session.async_shutdown)

    async def _async_poll_data() -> SensorUpdate:
        update = await session.async_poll()
        bt_coordinator.async_publish_poll(update)
        return update

    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    poll_coordinator = DataUpdateCoordinator[SensorUpdate](
        hass,
        _LOGGER,
        config_entry=entry,
        name=DOMAIN,
        update_method=_async_poll_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    entry.runtime_data = bt_coordinator
    entry.runtime_data.poll_coordinator = poll_coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # only start after all platforms have had a chance to subscribe
    entry.async_on_unload(bt_coordinator.async_start())

    # Keep a listener registered on poll_coordinator so DataUpdateCoordinator schedules periodic refreshes
    entry.async_on_unload(
        poll_coordinator.async_add_listener(bt_coordinator.async_update_poll_status)
    )

    # Reload entry when options change
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Don't block setup if the first poll fails (BLE device may be momentarily
    # unreachable). Entities load and recover on the next successful poll.
    await poll_coordinator.async_refresh()
    return True


async def async_reload_entry(hass: HomeAssistant, entry: VsonConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: VsonConfigEntry) -> bool:
    """Unload a config entry."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry_data["session"].async_shutdown()
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
