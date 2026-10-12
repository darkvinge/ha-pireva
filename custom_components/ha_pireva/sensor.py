"""Sensor för att visa nästa tomningsdatum från Pireva."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .api import normalize_address
from .const import DOMAIN
from .coordinator import PirevaCoordinator

if TYPE_CHECKING:
    from . import PirevaConfigEntry

ICONS = {
    "Restavfall": "mdi:trash-can",
    "Matavfall": "mdi:food-apple",
}
DEFAULT_ICON = "mdi:calendar-clock"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: PirevaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sätt upp sensorer från en config entry."""
    async_add_entities([PirevaWasteSensor(config_entry.runtime_data)])


class PirevaWasteSensor(CoordinatorEntity[PirevaCoordinator], SensorEntity):
    """Sensor för nästa tömning enligt Pirevas tomningsschema."""

    _attr_device_class = SensorDeviceClass.DATE

    def __init__(self, coordinator: PirevaCoordinator) -> None:
        """Initiera sensorn."""
        super().__init__(coordinator)
        slug = normalize_address(coordinator.address)
        self._attr_name = f"Pireva Avfallsschema {slug}-{coordinator.number}"
        self._attr_unique_id = f"{DOMAIN}_{slug}_{coordinator.number}"

    @property
    def native_value(self) -> date | None:
        """Returnerar nästa tömningsdatum."""
        upcoming = self.coordinator.upcoming
        return upcoming[0].date if upcoming else None

    @property
    def icon(self) -> str:
        """Returnerar ikonen baserat på avfallstyp."""
        upcoming = self.coordinator.upcoming
        if not upcoming:
            return DEFAULT_ICON
        return ICONS.get(upcoming[0].waste_type, DEFAULT_ICON)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Returnerar sensorns attribut."""
        upcoming = self.coordinator.upcoming
        if not upcoming:
            return {}

        first = upcoming[0]
        attributes: dict[str, Any] = {
            "avfallstyp": first.waste_type,
            "dagar_till_tomning": (first.date - dt_util.now().date()).days,
        }
        if len(upcoming) > 1:
            second = upcoming[1]
            attributes["efterfoljande_datum"] = second.date.isoformat()
            attributes["efterfoljande_avfallstyp"] = second.waste_type
        return attributes

    async def async_added_to_hass(self) -> None:
        """Räkna om nästa tömning och dagar kvar strax efter midnatt."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_track_time_change(
                self.hass, self._handle_midnight, hour=0, minute=0, second=5
            )
        )

    @callback
    def _handle_midnight(self, _now: datetime) -> None:
        self.async_write_ha_state()
