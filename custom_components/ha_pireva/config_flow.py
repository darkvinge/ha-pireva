"""Konfigurationsflöde för Pireva Tomningsschema."""
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN
from .sensor import normalize_address

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
                normalized = normalize_address(user_input["address"])
                number = user_input["number"]
                url = f"https://www.pireva.se/tomningsschema/{normalized}-{number}/?output=json"

                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                            if resp.status != 200:
                                errors["base"] = "invalid_address"
                            else:
                                data = await resp.json()
                                if not isinstance(data, list) or not data:
                                    errors["base"] = "invalid_address"
                except aiohttp.ClientError:
                    errors["base"] = "cannot_connect"

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