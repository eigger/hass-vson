"""Support for Vson binary sensors."""

from __future__ import annotations

from blesession import SessionReports

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN
from .entity import vson_device_info
from .types import VsonConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VsonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Vson BLE binary sensors."""
    connection_coordinator = hass.data[DOMAIN][entry.entry_id].get(
        "connection_coordinator"
    )
    if connection_coordinator is not None:
        address = hass.data[DOMAIN][entry.entry_id]["address"]
        async_add_entities(
            [VsonConnectionBinarySensorEntity(address, connection_coordinator)]
        )

    entry_data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            VsonProblemBinarySensorEntity(
                entry_data["address"], entry_data["reports_coordinator"]
            )
        ]
    )


class VsonConnectionBinarySensorEntity(
    CoordinatorEntity[DataUpdateCoordinator[bool]],
    BinarySensorEntity,
):
    """Diagnostic binary sensor for the active BLE poll connection."""

    _attr_has_entity_name = True
    _attr_translation_key = "connection"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        address: str,
        coordinator: DataUpdateCoordinator[bool],
    ) -> None:
        super().__init__(coordinator)
        self._address = address
        self._attr_unique_id = f"{address}_connection"
        self._attr_device_info = vson_device_info(address)

    @property
    def is_on(self) -> bool:
        """Return true while an active BLE polling connection is open."""
        return bool(self.coordinator.data)

    @property
    def icon(self) -> str:
        """Return icon based on connection state."""
        return "mdi:bluetooth-connect" if self.is_on else "mdi:bluetooth-off"


class VsonProblemBinarySensorEntity(
    CoordinatorEntity[DataUpdateCoordinator[SessionReports]], BinarySensorEntity
):
    """Latest session problem, kept available while polling fails."""

    _attr_has_entity_name = True
    _attr_translation_key = "problem"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, address: str, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{address}_problem"
        self._attr_device_info = vson_device_info(address)

    @property
    def is_on(self) -> bool | None:
        """No result is unknown; a successful subsequent poll clears the problem."""
        report = self.coordinator.data.last
        if report is None:
            return None
        return bool(report.get("error") or report.get("disconnect_error"))

    @property
    def extra_state_attributes(self):
        """Publish the latest outcome, including cleanup warnings."""
        return dict(self.coordinator.data.last or {})
