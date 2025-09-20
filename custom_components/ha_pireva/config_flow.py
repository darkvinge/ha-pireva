"""Konfigurationsflöde för Pireva Tomningsschema."""

import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class PirevaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handlar om konfigurationsflödet för Pireva Tomningsschema."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Hantera första steget i konfigurationsflödet."""
        errors = {}
        if user_input is not None:
            if not user_input.get("address"):
                errors["address"] = "required"
            if not user_input.get("number"):
                errors["number"] = "required"
            
            if not errors:
                return self.async_create_entry(
                    title="Pireva Tomningsschema",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("address"): str,
                vol.Required("number"): str,
            }),
            errors=errors,
        )