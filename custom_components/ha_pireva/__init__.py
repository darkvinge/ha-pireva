"""Integration för Pireva-tomningsscheman."""

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .sensor import normalize_address

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Sätt upp Pireva från en config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    
    # Skapa en referens till din sensor-entitet efter att den har skapats
    normalized_address = normalize_address(entry.data.get('address'))
    clean_id_part = normalized_address.replace('-', '_')
    unique_id = f"pireva_avfallsschema_{clean_id_part}_{entry.data.get('number')}"
    entity_id = f"sensor.{unique_id}"


    # Anropa uppdateringstjänsten direkt för att tvinga en första datahämtning
    await hass.services.async_call(
        "homeassistant",
        "update_entity",
        {"entity_id": entity_id},
        blocking=True,
    )
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unloadar en config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    return unload_ok