"""The Vson Bluetooth integration."""

from __future__ import annotations

from functools import partial
import logging
from .vson_ble import VsonBluetoothDeviceData, SensorUpdate
from homeassistant.components.bluetooth import (
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
    async_ble_device_from_address,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceRegistry
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .ble_session import vson_poll_ble_telemetry
from .const import DOMAIN
from .coordinator import VsonPassiveBluetoothProcessorCoordinator
from .types import VsonConfigEntry

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

def process_service_info(
    hass: HomeAssistant,
    entry: VsonConfigEntry,
    device_registry: DeviceRegistry,
    service_info: BluetoothServiceInfoBleak,
) -> SensorUpdate:
    """Process a BluetoothServiceInfoBleak, running side effects and returning sensor data."""
    coordinator = entry.runtime_data
    data = coordinator.device_data
    update = data.update(service_info)

    return update


async def async_setup_entry(hass: HomeAssistant, entry: VsonConfigEntry) -> bool:
    """Set up Vson Bluetooth from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    address = entry.unique_id
    assert address is not None

    data = VsonBluetoothDeviceData()
    hass.data[DOMAIN][entry.entry_id] = {}
    hass.data[DOMAIN][entry.entry_id]['address'] = address
    hass.data[DOMAIN][entry.entry_id]['data'] = data

    device_registry = dr.async_get(hass)
    bt_coordinator = VsonPassiveBluetoothProcessorCoordinator(
        hass,
        _LOGGER,
        address=address,
        mode=BluetoothScanningMode.PASSIVE,
        update_method=partial(process_service_info, hass, entry, device_registry),
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

    async def _async_poll_data(hass: HomeAssistant, entry: VsonConfigEntry) -> SensorUpdate:
        try:
            device = async_ble_device_from_address(hass, hass.data[DOMAIN][entry.entry_id]['address'])
            if not device:
                raise UpdateFailed("BLE Device none")
            coordinator: VsonPassiveBluetoothProcessorCoordinator = entry.runtime_data
            entry_data = hass.data[DOMAIN][entry.entry_id]
            async with vson_poll_ble_telemetry(entry_data):
                update = await coordinator.device_data.async_poll(device)
            coordinator.async_set_updated_data(update)
            return update
        except Exception as err:
            raise UpdateFailed(f"polling error: {err}") from err

    poll_coordinator = DataUpdateCoordinator[SensorUpdate](
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=partial(_async_poll_data, hass, entry),
        update_interval=timedelta(minutes=5),
    )
    
    entry.runtime_data = bt_coordinator
    entry.runtime_data.poll_coordinator = poll_coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # only start after all platforms have had a chance to subscribe
    entry.async_on_unload(bt_coordinator.async_start())

    # Don't block setup if the first poll fails (BLE device may be momentarily
    # unreachable). Entities load and recover on the next successful poll.
    await poll_coordinator.async_refresh()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: VsonConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)