"""The Wp6003 Bluetooth integration."""

from __future__ import annotations

from functools import partial
import logging
from asyncio import sleep, Lock
from .wp6003_ble import Wp6003BluetoothDeviceData, SensorUpdate
from homeassistant.components.bluetooth import (
    DOMAIN as BLUETOOTH_DOMAIN,
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
    async_ble_device_from_address,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, CoreState
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceRegistry
from homeassistant.util.signal_type import SignalType
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_DISCOVERED_EVENT_CLASSES,
    DOMAIN,
    Wp6003BleEvent,
)
from .coordinator import Wp6003ActiveBluetoothProcessorCoordinator
from .types import Wp6003ConfigEntry

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.EVENT, Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

def process_service_info(
    hass: HomeAssistant,
    entry: Wp6003ConfigEntry,
    device_registry: DeviceRegistry,
    service_info: BluetoothServiceInfoBleak,
) -> SensorUpdate:
    """Process a BluetoothServiceInfoBleak, running side effects and returning sensor data."""
    coordinator = entry.runtime_data
    data = coordinator.device_data
    update = data.update(service_info)

    return update


def format_event_dispatcher_name(
    address: str, event_class: str
) -> SignalType[Wp6003BleEvent]:
    """Format an event dispatcher name."""
    return SignalType(f"{DOMAIN}_event_{address}_{event_class}")


def format_discovered_event_class(address: str) -> SignalType[str, Wp6003BleEvent]:
    """Format a discovered event class."""
    return SignalType(f"{DOMAIN}_discovered_event_class_{address}")


async def async_setup_entry(hass: HomeAssistant, entry: Wp6003ConfigEntry) -> bool:
    """Set up Wp6003 Bluetooth from a config entry."""

    address = entry.unique_id
    assert address is not None

    data = Wp6003BluetoothDeviceData()

    def _needs_poll(
        service_info: BluetoothServiceInfoBleak, last_poll: float | None
    ) -> bool:
        # Only poll if hass is running, we need to poll,
        # and we actually have a way to connect to the device
        return (
            hass.state is CoreState.running
            and data.poll_needed(service_info, last_poll)
            and bool(
                async_ble_device_from_address(
                    hass, service_info.device.address, connectable=True
                )
            )
        )

    async def _async_poll(service_info: BluetoothServiceInfoBleak) -> SensorUpdate:
        # BluetoothServiceInfoBleak is defined in HA, otherwise would just pass it
        # directly to the Xiaomi code
        # Make sure the device we have is one that we can connect with
        # in case its coming from a passive scanner
        if service_info.connectable:
            connectable_device = service_info.device
        elif device := async_ble_device_from_address(
            hass, service_info.device.address, True
        ):
            connectable_device = device
        else:
            # We have no bluetooth controller that is in range of
            # the device to poll it
            raise RuntimeError(
                f"No connectable device found for {service_info.device.address}"
            )
        return await data.async_poll(connectable_device)
    
    device_registry = dr.async_get(hass)
    event_classes = set(entry.data.get(CONF_DISCOVERED_EVENT_CLASSES, ()))
    coordinator = Wp6003ActiveBluetoothProcessorCoordinator(
        hass,
        _LOGGER,
        address=address,
        mode=BluetoothScanningMode.PASSIVE,
        update_method=partial(process_service_info, hass, entry, device_registry),
        needs_poll_method=_needs_poll,
        device_data=data,
        discovered_event_classes=event_classes,
        poll_method=_async_poll,
        connectable=True,
        entry=entry,
    )
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # only start after all platforms have had a chance to subscribe
    entry.async_on_unload(coordinator.async_start())
    return True


async def async_unload_entry(hass: HomeAssistant, entry: Wp6003ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

async def get_entry_id_from_device(hass, device_id: str) -> str:
    device_reg = dr.async_get(hass)
    device_entry = device_reg.async_get(device_id)
    if not device_entry:
        raise ValueError(f"Unknown device_id: {device_id}")
    if not device_entry.config_entries:
        raise ValueError(f"No config entries for device {device_id}")

    _LOGGER.debug(f"{device_id} to {device_entry.config_entries}")
    try:
        entry_id = next(iter(device_entry.config_entries))
    except StopIteration:
        _LOGGER.error("%s None", device_id)
        return None

    return entry_id