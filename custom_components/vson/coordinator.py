"""The Vson Bluetooth integration."""

from collections.abc import Callable
from logging import Logger

from .vson_ble import VsonBluetoothDeviceData, SensorUpdate

from homeassistant.components.bluetooth import (
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
)
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothProcessorCoordinator,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .types import VsonConfigEntry


class VsonPassiveBluetoothProcessorCoordinator(
    PassiveBluetoothProcessorCoordinator[SensorUpdate]
):
    """Define a Vson Bluetooth Passive Update Processor Coordinator."""

    poll_coordinator: DataUpdateCoordinator[SensorUpdate]

    def __init__(
        self,
        hass: HomeAssistant,
        logger: Logger,
        address: str,
        mode: BluetoothScanningMode,
        update_method: Callable[[BluetoothServiceInfoBleak], SensorUpdate],
        device_data: VsonBluetoothDeviceData,
        entry: VsonConfigEntry,
        connectable: bool = True,
    ) -> None:
        """Initialize the Vson Bluetooth Passive Update Processor Coordinator."""
        super().__init__(hass, logger, address, mode, update_method, connectable)
        self.device_data = device_data
        self.entry = entry
        self.processors: list[PassiveBluetoothDataProcessor] = []

    @property
    def available(self) -> bool:
        """Active measurements remain available until the next poll fails."""
        poll = self.poll_coordinator
        return poll.last_update_success and poll.data is not None

    @callback
    def async_register_processor(
        self,
        processor: PassiveBluetoothDataProcessor,
        entity_description_class: type[EntityDescription] | None = None,
    ) -> Callable[[], None]:
        """Track processors through the public HA registration API."""
        remove = super().async_register_processor(processor, entity_description_class)
        self.processors.append(processor)

        @callback
        def unregister() -> None:
            self.processors.remove(processor)
            remove()

        return unregister

    @callback
    def async_publish_poll(self, update: SensorUpdate) -> None:
        """Dispatch active readings through the processor's public API."""
        for processor in self.processors:
            processor.async_handle_update(update, False)

    @callback
    def async_update_poll_status(self) -> None:
        """Refresh availability even if a failed poll produced no readings."""
        for processor in self.processors:
            processor.async_update_listeners(None)


class VsonPassiveBluetoothDataProcessor[_T](
    PassiveBluetoothDataProcessor[_T, SensorUpdate]
):
    """Define a Vson Bluetooth Passive Update Data Processor."""

    coordinator: VsonPassiveBluetoothProcessorCoordinator
