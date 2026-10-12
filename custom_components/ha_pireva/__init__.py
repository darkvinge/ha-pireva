"""Integration för Pireva-tomningsscheman."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import normalize_address
from .const import CONF_ADDRESS, CONF_NUMBER

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Sätt upp Pireva från en config entry."""
    # Poster skapade av äldre versioner saknar unikt id, vilket gör att
    # dubblettkontrollen i konfigurationsflödet inte hittar dem.
    if entry.unique_id is None:
        address = entry.data.get(CONF_ADDRESS, "")
        number = str(entry.data.get(CONF_NUMBER, "")).strip().lower()
        hass.config_entries.async_update_entry(
            entry, unique_id=f"{normalize_address(address)}_{number}"
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unloadar en config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
