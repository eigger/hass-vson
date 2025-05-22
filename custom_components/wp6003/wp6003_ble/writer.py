# wp6003_ble.py

from __future__ import annotations
from enum import Enum
import logging
import struct
import traceback
from typing import Any, Callable, TypeVar
from asyncio import Event, wait_for, sleep
from PIL import Image
from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection

_LOGGER = logging.getLogger(__name__)

# 예외 정의
class BleakCharacteristicMissing(BleakError):
    """Characteristic Missing"""

class BleakServiceMissing(BleakError):
    """Service Missing"""

WrapFuncType = TypeVar("WrapFuncType", bound=Callable[..., Any])

def disconnect_on_missing_services(func: WrapFuncType) -> WrapFuncType:
    """Missing services"""
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except (BleakServiceMissing, BleakCharacteristicMissing):
            if self.client.is_connected:
                await self.client.clear_cache()
                await self.client.disconnect()
            raise
    return wrapper  # type: ignore

async def get_sensor_data(
    ble_device: BLEDevice,
) -> bool:
    client: BleakClient | None = None
    try:
        _LOGGER.debug("connection: %s", ble_device)
        client = await establish_connection(BleakClient, ble_device, ble_device.address)
        services = client.services
        _LOGGER.debug(f"services: {services}")
        return True
    except Exception as e:
        _LOGGER.error("Fail update: %s", e)
        _LOGGER.error(traceback.print_exc())
        return False
    finally:
        if client and client.is_connected:
            await client.disconnect()

class Wp6003Client:
       
    def __init__(
        self,
        client: BleakClient,
        uuids: list[str],
    ) -> None:
        self.client = client
        self.cmd_uuid, self.img_uuid = uuids[:2]
        self.event: Event = Event()
        self.command_data: bytes | None = None

    @disconnect_on_missing_services
    async def start_notify(self) -> None:
        await self.client.start_notify(self.cmd_uuid, self._notification_handler)
        await sleep(0.5)

    @disconnect_on_missing_services
    async def stop_notify(self) -> None:
        await self.client.stop_notify(self.cmd_uuid)

    @disconnect_on_missing_services
    async def write(self, uuid: str, data: bytes) -> None:
        _LOGGER.debug("Write UUID=%s data=%s", uuid, len(data))
        chunk = len(data)
        for i in range(0, len(data), chunk):
            await self.client.write_gatt_char(uuid, data[i : i + chunk])
            await sleep(0.05)

    def _notification_handler(self, _: Any, data: bytearray) -> None:
        if self.command_data == None:
            self.command_data = bytes(data)
            self.event.set()

    async def read(self, timeout: float = 5.0) -> bytes:
        await wait_for(self.event.wait(), timeout)
        data = self.command_data or b""
        _LOGGER.debug("Received: %s", data.hex())
        return data

    async def write_with_response(self, uuid, packet: bytes) -> bytes:
        self.command_data = None
        self.event.clear()
        await self.write(uuid, packet)
        return await self.read()
    