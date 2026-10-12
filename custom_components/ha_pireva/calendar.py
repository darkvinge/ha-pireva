"""Kalender med kommande tömningar från Pireva."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .api import Pickup, normalize_address
from .const import DOMAIN
from .coordinator import PirevaCoordinator

if TYPE_CHECKING:
    from . import PirevaConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: PirevaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sätt upp kalendern från en config entry."""
    async_add_entities([PirevaCalendar(config_entry.runtime_data)])


def _to_event(pickup: Pickup) -> CalendarEvent:
    """Gör om en tömning till en heldagshändelse."""
    return CalendarEvent(
        start=pickup.date,
        end=pickup.date + timedelta(days=1),
        summary=pickup.waste_type,
        uid=f"{pickup.date.isoformat()}_{pickup.waste_type}",
    )


class PirevaCalendar(CoordinatorEntity[PirevaCoordinator], CalendarEntity):
    """Kalender med Pirevas tömningar som heldagshändelser."""

    _attr_icon = "mdi:delete-empty"

    def __init__(self, coordinator: PirevaCoordinator) -> None:
        """Initiera kalendern."""
        super().__init__(coordinator)
        slug = normalize_address(coordinator.address)
        self._attr_name = f"Pireva Avfallsschema {slug}-{coordinator.number}"
        self._attr_unique_id = f"{DOMAIN}_{slug}_{coordinator.number}_calendar"

    @property
    def event(self) -> CalendarEvent | None:
        """Returnerar pågående eller nästa tömning."""
        upcoming = self.coordinator.upcoming
        return _to_event(upcoming[0]) if upcoming else None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Returnerar tömningar som överlappar det efterfrågade intervallet."""
        events = []
        for pickup in self.coordinator.data or []:
            event_start = dt_util.start_of_local_day(pickup.date)
            event_end = event_start + timedelta(days=1)
            if event_start < end_date and event_end > start_date:
                events.append(_to_event(pickup))
        return events
