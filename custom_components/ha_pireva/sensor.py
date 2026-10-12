"""Sensor för att visa nästa tomningsdatum från Pireva."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .api import Pickup, PirevaError, async_fetch_schedule, normalize_address
from .const import CONF_ADDRESS, CONF_NUMBER, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=6)

ICONS = {
    "Restavfall": "mdi:trash-can",
    "Matavfall": "mdi:food-apple",
}
DEFAULT_ICON = "mdi:calendar-clock"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sätt upp sensorer från en config entry."""
    address = config_entry.data.get(CONF_ADDRESS)
    number = config_entry.data.get(CONF_NUMBER)

    if not address or not number:
        _LOGGER.error("Adress eller nummer saknas i konfigurationen.")
        return

    async_add_entities(
        [PirevaWasteSensor(hass, address, number)],
        update_before_add=True,
    )


class PirevaWasteSensor(SensorEntity):
    """Sensor för nästa tömning enligt Pirevas tomningsschema."""

    _attr_device_class = SensorDeviceClass.DATE

    def __init__(self, hass: HomeAssistant, address: str, number: str) -> None:
        """Initiera sensorn."""
        self._session = async_get_clientsession(hass)
        self._address = address
        self._number = number
        self._pickups: list[Pickup] = []

        slug = normalize_address(address)
        self._attr_name = f"Pireva Avfallsschema {slug}-{number}"
        self._attr_unique_id = f"{DOMAIN}_{slug}_{number}"

    @property
    def native_value(self) -> date | None:
        """Returnerar nästa tömningsdatum."""
        return self._pickups[0].date if self._pickups else None

    @property
    def icon(self) -> str:
        """Returnerar ikonen baserat på avfallstyp."""
        if not self._pickups:
            return DEFAULT_ICON
        return ICONS.get(self._pickups[0].waste_type, DEFAULT_ICON)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Returnerar sensorns attribut."""
        if not self._pickups:
            return {}

        first = self._pickups[0]
        attributes: dict[str, Any] = {
            "avfallstyp": first.waste_type,
            "dagar_till_tomning": (first.date - dt_util.now().date()).days,
        }
        if len(self._pickups) > 1:
            second = self._pickups[1]
            attributes["efterfoljande_datum"] = second.date.isoformat()
            attributes["efterfoljande_avfallstyp"] = second.waste_type
        return attributes

    async def async_added_to_hass(self) -> None:
        """Räkna om dagar kvar strax efter midnatt."""
        self.async_on_remove(
            async_track_time_change(
                self.hass, self._handle_midnight, hour=0, minute=0, second=5
            )
        )

    @callback
    def _handle_midnight(self, _now: datetime) -> None:
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Hämtar den senaste datan från API:et."""
        try:
            pickups = await async_fetch_schedule(
                self._session, self._address, self._number
            )
        except PirevaError as err:
            _LOGGER.error("Fel vid hämtning av tomningsschema: %s", err)
            self._attr_available = False
            return

        if not pickups:
            _LOGGER.warning("API-svaret innehöll inga tömningar.")
            self._attr_available = False
            return

        today = dt_util.now().date()
        self._pickups = [p for p in pickups if p.date >= today] or pickups
        self._attr_available = True
