"""Tester för konfigurationsflödet."""

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.ha_pireva.const import DOMAIN

from .conftest import ADDRESS, NUMBER, UNIQUE_ID, URL

INVALID_URL = "https://www.pireva.se/tomningsschema/finns-inte-9/?output=json"
USER_INPUT = {"address": ADDRESS, "number": NUMBER}


async def _start_flow(hass):
    return await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )


async def test_create_entry(hass, aioclient_mock, schedule):
    aioclient_mock.get(URL, json=schedule)
    result = await _start_flow(hass)
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"address": f" {ADDRESS} ", "number": NUMBER}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == f"{ADDRESS} {NUMBER}"
    assert result["data"] == USER_INPUT
    assert result["result"].unique_id == UNIQUE_ID


async def test_invalid_address(hass, aioclient_mock):
    aioclient_mock.get(INVALID_URL, status=404, text="<html></html>")
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"address": "Finns inte", "number": "9"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_address"}


async def test_empty_schedule(hass, aioclient_mock):
    aioclient_mock.get(URL, json=[])
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["errors"] == {"base": "invalid_address"}


async def test_cannot_connect(hass, aioclient_mock):
    aioclient_mock.get(URL, status=500)
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["errors"] == {"base": "cannot_connect"}


async def test_required_fields(hass):
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"address": "  ", "number": ""}
    )
    assert result["errors"] == {"address": "required", "number": "required"}


async def test_already_configured(hass, config_entry):
    config_entry.add_to_hass(hass)
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"address": ADDRESS.upper(), "number": NUMBER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
