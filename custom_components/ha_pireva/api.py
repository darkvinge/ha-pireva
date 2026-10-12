"""API-klient för Pireva Tomningsschema."""

from __future__ import annotations

import asyncio
import re
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime

import aiohttp

URL_TEMPLATE = "https://www.pireva.se/tomningsschema/{address}-{number}/?output=json"
TIMEOUT = aiohttp.ClientTimeout(total=10)


class PirevaError(Exception):
    """Basklass för fel från Pireva."""


class PirevaConnectionError(PirevaError):
    """Kunde inte hämta data från Pireva."""


class PirevaInvalidAddressError(PirevaError):
    """Adressen finns inte hos Pireva."""


@dataclass(frozen=True)
class Pickup:
    """En planerad tömning."""

    date: date
    waste_type: str


def normalize_address(address: str) -> str:
    """Normaliserar en adress till formatet Pireva använder i URL:en."""
    # Ta bort diakritiska tecken (å -> a, ä -> a, ö -> o, é -> e, ...)
    decomposed = unicodedata.normalize("NFKD", address.strip().lower())
    ascii_only = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"\s+", "-", ascii_only)


def build_url(address: str, number: str) -> str:
    """Bygger URL:en till tömningsschemat för en adress."""
    return URL_TEMPLATE.format(
        address=normalize_address(address),
        number=str(number).strip().lower(),
    )


async def async_fetch_schedule(
    session: aiohttp.ClientSession, address: str, number: str
) -> list[Pickup]:
    """Hämtar kommande tömningar för en adress, sorterade på datum."""
    url = build_url(address, number)
    try:
        async with session.get(url, timeout=TIMEOUT) as resp:
            if resp.status == 404:
                raise PirevaInvalidAddressError(url)
            if resp.status != 200:
                raise PirevaConnectionError(f"HTTP {resp.status} från {url}")
            data = await resp.json(content_type=None)
    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
        raise PirevaConnectionError(str(err) or type(err).__name__) from err

    if not isinstance(data, list):
        raise PirevaConnectionError("Oväntat format på API-svaret")

    pickups = []
    for item in data:
        if not isinstance(item, dict):
            continue
        try:
            pickup_date = datetime.strptime(item["date"], "%Y-%m-%d").date()
            waste_type = str(item["waste_type"])
        except (KeyError, TypeError, ValueError):
            continue
        pickups.append(Pickup(pickup_date, waste_type))

    return sorted(pickups, key=lambda p: p.date)
