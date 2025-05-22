"""The Wp6003 Bluetooth integration."""

from collections.abc import Callable, Coroutine
from logging import Logger
from typing import Any

from .wp6003_ble import Wp6003BluetoothDeviceData, SensorUpdate

from homeassistant.components.bluetooth import (
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
)
from homeassistant.components.bluetooth.active_update_processor import (
    ActiveBluetoothProcessorCoordinator,
)
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer

from .types import Wp6003ConfigEntry


class Wp6003ActiveBluetoothProcessorCoordinator(
    ActiveBluetoothProcessorCoordinator[SensorUpdate]
):
    """Define a Wp6003 Bluetooth Passive Update Processor Coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: Logger,
        *,
        address: str,
        mode: BluetoothScanningMode,
        update_method: Callable[[BluetoothServiceInfoBleak], SensorUpdate],
        needs_poll_method: Callable[[BluetoothServiceInfoBleak, float | None], bool],
        device_data: Wp6003BluetoothDeviceData,
        discovered_event_classes: set[str],
        poll_method: Callable[
            [BluetoothServiceInfoBleak],
            Coroutine[Any, Any, SensorUpdate],
        ]
        | None = None,
        poll_debouncer: Debouncer[Coroutine[Any, Any, None]] | None = None,
        entry: Wp6003ConfigEntry,
        connectable: bool = True,
    ) -> None:
        """Initialize the Wp6003 Bluetooth Passive Update Processor Coordinator."""
        super().__init__(            
            hass=hass,
            logger=logger,
            address=address,
            mode=mode,
            update_method=update_method,
            needs_poll_method=needs_poll_method,
            poll_method=poll_method,
            poll_debouncer=poll_debouncer,
            connectable=connectable,
        )
        self.discovered_event_classes = discovered_event_classes
        self.device_data = device_data
        self.entry = entry


class Wp6003PassiveBluetoothDataProcessor[_T](
    PassiveBluetoothDataProcessor[_T, SensorUpdate]
):
    """Define a Wp6003 Bluetooth Passive Update Data Processor."""

    coordinator: Wp6003ActiveBluetoothProcessorCoordinator
