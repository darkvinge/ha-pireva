"""Gemensam datahämtning för Pireva Tomningsschema."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import Pickup, PirevaError, async_fetch_schedule
from .const import CONF_ADDRESS, CONF_NUMBER, DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(hours=6)


class PirevaCoordinator(DataUpdateCoordinator[list[Pickup]]):
    """Hämtar tomningsschemat en gång och delar det mellan entiteterna."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initiera coordinatorn."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=UPDATE_INTERVAL,
        )
        self.address: str = entry.data[CONF_ADDRESS]
        self.number: str = entry.data[CONF_NUMBER]
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> list[Pickup]:
        """Hämtar alla tömningar från API:et."""
        try:
            pickups = await async_fetch_schedule(
                self._session, self.address, self.number
            )
        except PirevaError as err:
            raise UpdateFailed(f"Fel vid hämtning av tomningsschema: {err}") from err

        if not pickups:
            raise UpdateFailed("API-svaret innehöll inga tömningar")
        return pickups

    @property
    def upcoming(self) -> list[Pickup]:
        """Returnerar tömningar från och med i dag."""
        today = dt_util.now().date()
        return [p for p in self.data or [] if p.date >= today]
