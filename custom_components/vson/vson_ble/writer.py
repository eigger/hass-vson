"""WP6003 commands over the shared BLE session and notification transport."""

from __future__ import annotations

from collections.abc import Callable

from bleak.backends.device import BLEDevice
from blesession import (
    DeviceError,
    GattMismatch,
    Notifications,
    SessionTrace,
    ble_session,
    characteristic_or_raise,
)

from .const import CHAR_CMD, CHAR_NOTI, SERVICE_WP6003

NOTIFY_SETTLE_S = 0.5
WRITE_PACE_S = 0.05
REPLY_TIMEOUT_S = 5.0


class InvalidSensorResponse(DeviceError):
    """The WP6003 returned a packet that cannot be parsed."""

    retryable = False


async def get_sensor_data(
    ble_device: BLEDevice,
    *,
    trace: SessionTrace | None = None,
    on_connection: Callable[[bool], None] | None = None,
) -> bytes:
    """Read one measurement, preserving transport and protocol failures."""
    trace = trace if trace is not None else SessionTrace()

    def disconnected(_client: object) -> None:
        if on_connection is not None:
            on_connection(False)

    try:
        async with ble_session(
            ble_device, trace=trace, name="WP6003", disconnected_callback=disconnected
        ) as client:
            if on_connection is not None:
                on_connection(True)
            with trace.timed("subscribe"):
                characteristic_or_raise(
                    client,
                    SERVICE_WP6003,
                    CHAR_NOTI,
                    properties=("notify",),
                    label="WP6003",
                )
                command = characteristic_or_raise(
                    client,
                    SERVICE_WP6003,
                    CHAR_CMD,
                    label="WP6003",
                )
                if not {"write", "write-without-response"}.intersection(
                    command.properties
                ):
                    raise GattMismatch("WP6003 command characteristic is not writable")
            async with Notifications(
                client, CHAR_NOTI, settle=NOTIFY_SETTLE_S
            ) as replies:
                with trace.timed("readout"):
                    data = await replies.request(
                        CHAR_CMD,
                        b"\xab",
                        timeout=REPLY_TIMEOUT_S,
                        step="readout",
                        response=None,
                        pace_s=WRITE_PACE_S,
                    )
                    if len(data) != 18:
                        raise InvalidSensorResponse(
                            f"WP6003 returned {len(data)} bytes; expected 18"
                        )
                    trace.note(payload_bytes=len(data))
                    return data
    finally:
        if on_connection is not None:
            on_connection(False)
