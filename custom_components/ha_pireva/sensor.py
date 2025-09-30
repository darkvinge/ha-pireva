"""Sensor för att visa nästa tomningsdatum från Pireva."""

import logging
from datetime import timedelta
import aiohttp
from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=6)

def normalize_address(address):
    """Normaliserar en sträng genom att ersätta specialtecken."""
    return (
        address.lower()
        .replace("å", "a")
        .replace("ä", "a")
        .replace("ö", "o")
        .replace(" ", "-")
    )

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Sätt upp sensorer från en config entry."""
    address = config_entry.data.get("address")
    number = config_entry.data.get("number")

    if not address or not number:
        _LOGGER.error("Adress eller nummer saknas i konfigurationen.")
        return

    normalized_address = normalize_address(address)
    resource_url = f"https://www.pireva.se/tomningsschema/{normalized_address}-{number}/?output=json"

    async_add_entities([PirevaWasteSensor(hass, resource_url, address, number)])


class PirevaWasteSensor(Entity):
    """Anpassad sensor för Pireva tomningsschema."""
    
    _attr_scan_interval = SCAN_INTERVAL

    def __init__(self, hass, resource_url, address, number):
        """Initiera sensorn."""
        self.hass = hass
        self._resource = resource_url
        self._address = normalize_address(address)
        self._number = number
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Returnerar namnet på sensorn."""
        return f"Pireva Avfallsschema {self._address}-{self._number}"

    @property
    def state(self):
        """Returnerar sensorns tillstånd (nästa tömningsdatum)."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Returnerar sensorns attribut."""
        return self._attributes
    
    @property
    def unique_id(self):
        """Returnerar en unik ID för entiteten."""
        return f"{DOMAIN}_{self._address}_{self._number}"

    async def async_update(self):
        """Hämtar den senaste datan från API:et."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self._resource, timeout=10) as response:
                    if response.status != 200:
                        _LOGGER.error("Fel vid hämtning av data: Status %s", response.status)
                        return
                    
                    data = await response.json()
                    
                    if isinstance(data, list) and data:
                        json_object = data[0]
                    else:
                        _LOGGER.error("API-svaret är inte en lista med data eller är tomt.")
                        self._state = None
                        self._attributes = {}
                        return
                    
                    # Extrahera nästa tömningsdatum och avfallstyp från det nya objektet
                    # OBS: Ändra "data.get" till "json_object.get"
                    next_dump_date = json_object.get('date')
                    waste_type = json_object.get('waste_type')
                    
                    if next_dump_date and waste_type:
                        self._state = next_dump_date
                        self._attributes['avfallstyp'] = waste_type
                        
                        try:
                            from datetime import datetime, date
                            next_date_obj = datetime.strptime(next_dump_date, '%Y-%m-%d').date()
                            days_until = (next_date_obj - date.today()).days
                            self._attributes['dagar_till_tomning'] = days_until
                        except (ValueError, TypeError) as e:
                            _LOGGER.error("Kunde inte beräkna dagar till tömning: %s", e)
                            self._attributes['dagar_till_tomning'] = None
                    else:
                        _LOGGER.warning("Saknade 'date' eller 'waste_type' i API-svaret.")
                        self._state = None
                        self._attributes = {}
        except aiohttp.ClientError as err:
            _LOGGER.error("Fel vid API-anrop: %s", err)
            self._state = None
            self._attributes = {}

    @property
    def icon(self):
        """Returnerar ikonen baserat på avfallstyp."""
        if self._attributes.get('avfallstyp') == 'Restavfall':
            return 'mdi:trash-can'
        if self._attributes.get('avfallstyp') == 'Matavfall':
            return 'mdi:food-apple'
        return 'mdi:calendar-clock'
