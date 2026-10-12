"""Konfigurationsflöde för Pireva Tomningsschema."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    PirevaConnectionError,
    PirevaInvalidAddressError,
    async_fetch_schedule,
    normalize_address,
)
from .const import CONF_ADDRESS, CONF_NUMBER, DOMAIN


class PirevaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handlar om konfigurationsflödet för Pireva Tomningsschema."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Hantera första steget i konfigurationsflödet."""
        errors = {}

        if user_input is not None:
            address = user_input.get(CONF_ADDRESS, "").strip()
            number = user_input.get(CONF_NUMBER, "").strip()

            if not address:
                errors[CONF_ADDRESS] = "required"
            if not number:
                errors[CONF_NUMBER] = "required"

            if not errors:
                await self.async_set_unique_id(
                    f"{normalize_address(address)}_{number.lower()}"
                )
                self._abort_if_unique_id_configured()

                try:
                    pickups = await async_fetch_schedule(
                        async_get_clientsession(self.hass), address, number
                    )
                except PirevaInvalidAddressError:
                    errors["base"] = "invalid_address"
                except PirevaConnectionError:
                    errors["base"] = "cannot_connect"
                else:
                    if not pickups:
                        errors["base"] = "invalid_address"

            if not errors:
                return self.async_create_entry(
                    title=f"{address} {number}",
                    data={CONF_ADDRESS: address, CONF_NUMBER: number},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ADDRESS): str,
                vol.Required(CONF_NUMBER): str,
            }),
            errors=errors,
        )
