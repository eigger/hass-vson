"""HA polling policy and diagnostics backed by blesession's public API."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from time import perf_counter
from typing import Any

from homeassistant.core import HomeAssistant

from blesession import (
    Attempt,
    Failure,
    SessionReports,
    fallback_report,
    report_attempt,
    run_attempts,
    stages,
)
from blesession.hass import ble_device_or_raise, radio_facts
from homeassistant.helpers.update_coordinator import UpdateFailed

from .vson_ble import SensorUpdate, VsonBluetoothDeviceData
from .vson_ble.writer import InvalidSensorResponse

POLL_TIMEOUT_S = 60.0
STAGE_MAP = {"subscribe": stages.SESSION, "readout": stages.TRANSFER}


def likely_cause(failure: Failure) -> str | None:
    """Explain only WP6003 protocol errors; the library explains transport errors."""
    if isinstance(failure.exc, InvalidSensorResponse):
        return "WP6003 returned an invalid measurement. Check the model and firmware."
    return None


@asynccontextmanager
async def vson_poll_ble_telemetry(entry_data: dict[str, Any]) -> AsyncIterator[None]:
    """Publish elapsed poll time without mistaking polling for a GATT connection."""
    duration = entry_data["duration_coordinator"]
    started = perf_counter()

    async def ticker() -> None:
        while True:
            await asyncio.sleep(1)
            duration.async_set_updated_data(round(perf_counter() - started, 3))

    duration.async_set_updated_data(0.0)
    task = asyncio.create_task(ticker())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        duration.async_set_updated_data(round(perf_counter() - started, 3))
        entry_data["connection_coordinator"].async_set_updated_data(False)


class VsonBleSession:
    """One bounded poll per entry; retain failure evidence after recovery."""

    def __init__(
        self,
        hass: HomeAssistant,
        address: str,
        device_data: VsonBluetoothDeviceData,
        entry_data: dict[str, Any],
    ) -> None:
        self.hass = hass
        self.address = address
        self.device_data = device_data
        self.entry_data = entry_data
        self.reports = SessionReports()
        self.lock = asyncio.Lock()
        self._tasks: set[asyncio.Task] = set()
        self._stopped = False

    async def async_poll(self) -> SensorUpdate:
        """Resolve the current HA route under the attempt lock, then poll."""
        if self._stopped:
            raise asyncio.CancelledError
        task = asyncio.current_task()
        assert task is not None
        self._tasks.add(task)
        try:
            attempt = await run_attempts(
                self._poll_once,
                lock=self.lock,
                max_attempts=1,
                attempt_timeout_s=POLL_TIMEOUT_S,
                stage_map=STAGE_MAP,
                on_attempt=self._record,
                name="WP6003",
            )
            if attempt.error is not None:
                raise UpdateFailed(str(attempt.error)) from attempt.error
            assert attempt.result is not None
            return attempt.result
        finally:
            self._tasks.discard(task)

    async def _poll_once(self, attempt: Attempt[SensorUpdate]) -> SensorUpdate:
        async with vson_poll_ble_telemetry(self.entry_data):
            device = ble_device_or_raise(self.hass, self.address)
            return await self.device_data.async_poll(
                device,
                trace=attempt.trace,
                on_connection=self.entry_data[
                    "connection_coordinator"
                ].async_set_updated_data,
            )

    def _record(self, attempt: Attempt[SensorUpdate]) -> None:
        try:
            report = report_attempt(
                attempt,
                operation="poll",
                attempts=1,
                facts=radio_facts(self.hass, self.address, attempt.trace.link),
                cause=likely_cause,
                noun="WP6003",
            )
        except Exception:
            report = fallback_report("poll", attempt=attempt)
        self.reports.record(report)
        self.entry_data["reports_coordinator"].async_set_updated_data(self.reports)

    async def async_shutdown(self) -> None:
        """Cancel in-flight polls and await the library's connection cleanup."""
        self._stopped = True
        tasks = [task for task in self._tasks if task is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
