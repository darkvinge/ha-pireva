"""Tester för uppsättning, sensor och kalender."""

from datetime import timedelta

from homeassistant.config_entries import ConfigEntryState
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_pireva.const import DOMAIN

from .conftest import ADDRESS, CALENDAR_ID, NUMBER, SENSOR_ID, UNIQUE_ID, URL


async def test_sensor_and_calendar(hass, aioclient_mock, config_entry, schedule):
    aioclient_mock.get(URL, json=schedule)
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.LOADED
    # Sensor och kalender delar på ett anrop
    assert aioclient_mock.call_count == 1

    today = dt_util.now().date()
    sensor = hass.states.get(SENSOR_ID)
    assert sensor.state == (today + timedelta(days=1)).isoformat()
    assert sensor.attributes["avfallstyp"] == "Matavfall"
    assert sensor.attributes["dagar_till_tomning"] == 1
    assert sensor.attributes["efterfoljande_datum"] == (
        today + timedelta(days=8)
    ).isoformat()
    assert sensor.attributes["efterfoljande_avfallstyp"] == "Restavfall"
    assert sensor.attributes["icon"] == "mdi:food-apple"

    calendar = hass.states.get(CALENDAR_ID)
    assert calendar.state == "off"
    assert calendar.attributes["message"] == "Matavfall"
    assert calendar.attributes["all_day"] is True

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    assert config_entry.state is ConfigEntryState.NOT_LOADED


async def test_calendar_get_events(hass, aioclient_mock, config_entry, schedule):
    aioclient_mock.get(URL, json=schedule)
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    start = dt_util.start_of_local_day()
    response = await hass.services.async_call(
        "calendar",
        "get_events",
        {
            "entity_id": CALENDAR_ID,
            "start_date_time": start.isoformat(),
            "end_date_time": (start + timedelta(days=9)).isoformat(),
        },
        blocking=True,
        return_response=True,
    )
    events = response[CALENDAR_ID]["events"]
    assert [event["summary"] for event in events] == [
        "Matavfall",
        "Restavfall",
        "Matavfall",
    ]


async def test_setup_retry_when_api_fails(hass, aioclient_mock, config_entry):
    aioclient_mock.get(URL, status=500)
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_legacy_entry_gets_unique_id(hass, aioclient_mock, schedule):
    aioclient_mock.get(URL, json=schedule)
    entry = MockConfigEntry(
        domain=DOMAIN, data={"address": ADDRESS, "number": NUMBER}, unique_id=None
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.unique_id == UNIQUE_ID
