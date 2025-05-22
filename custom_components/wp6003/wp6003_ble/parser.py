from __future__ import annotations

import logging
from typing import Any
from bleak.backends.device import BLEDevice
from bluetooth_sensor_state_data import BluetoothData
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from home_assistant_bluetooth import BluetoothServiceInfoBleak
from sensor_state_data import (
    SensorLibrary,
    SensorUpdate,
)
from .const import SERVICE_WP6003, TIMEOUT_1DAY
from .writer import get_sensor_data
_LOGGER = logging.getLogger(__name__)

def to_mac(addr: bytes) -> str:
    """Return formatted MAC address."""
    return ":".join(f"{i:02X}" for i in addr)

class Wp6003BluetoothDeviceData(BluetoothData):
    """Data for BTHome Bluetooth devices."""

    def __init__(self) -> None:
        super().__init__()

        # The last service_info we saw that had a payload
        # We keep this to help in reauth flows where we want to reprocess and old
        # value with a new bindkey.
        self.last_service_info: BluetoothServiceInfoBleak | None = None

        self.pending = True


    def supported(self, data: BluetoothServiceInfoBleak) -> bool:
        if not super().supported(data):
            return False
        return True

    def _start_update(self, service_info: BluetoothServiceInfoBleak) -> None:
        """Update from BLE advertisement data."""
        #_LOGGER.debug(f"service_info: {service_info}")
        for uuid in service_info.service_uuids:
            if uuid == SERVICE_WP6003:
                if self._parse_wp6003(service_info):
                    self.last_service_info = service_info
        return None

    def _parse_wp6003(
        self, service_info: BluetoothServiceInfoBleak
    ) -> bool:
        """Parser for Wp6003 sensors"""

        model = "WP6003"
        manufacturer = "Vson"

        identifier = service_info.address.replace(":", "")[-8:]
        self.set_title(f"{identifier}")
        self.set_device_name(f"{identifier}")
        self.set_device_type(f"Air Quality Sensor")
        self.set_device_manufacturer(manufacturer)
        self.pending = False
        return True
    
    def poll_needed(
        self, service_info: BluetoothServiceInfo, last_poll: float | None
    ) -> bool:
        """
        This is called every time we get a service_info for a device. It means the
        device is working and online. If 24 hours has passed, it may be a good
        time to poll the device.
        """
        if self.pending:
            # Never need to poll if we are pending as we don't even know what
            # kind of device we are
            return False

        return not last_poll or last_poll > TIMEOUT_1DAY

    async def async_poll(self, ble_device: BLEDevice) -> SensorUpdate:
        """
        Poll the device to retrieve any values we can't get from passive listening.
        """
        _LOGGER.debug("async_poll")
        await get_sensor_data(ble_device)
        return self._finish_update()