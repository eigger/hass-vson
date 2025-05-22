"""The Wp6003 Bluetooth integration."""

from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry

if TYPE_CHECKING:
    from .coordinator import Wp6003ActiveBluetoothProcessorCoordinator

type Wp6003ConfigEntry = ConfigEntry[Wp6003ActiveBluetoothProcessorCoordinator]
