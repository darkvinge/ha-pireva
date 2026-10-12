"""Gemensamma fixtures för testerna."""

from datetime import timedelta

import pytest
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

# Importeras här så att vår custom_components laddas innan Home Assistant
# lägger till testverktygets egen custom_components-katalog i sys.path.
from custom_components.ha_pireva.const import CONF_ADDRESS, CONF_NUMBER, DOMAIN

ADDRESS = "Sundsgatan"
NUMBER = "41"
UNIQUE_ID = "sundsgatan_41"
URL = "https://www.pireva.se/tomningsschema/sundsgatan-41/?output=json"
SENSOR_ID = "sensor.pireva_avfallsschema_sundsgatan_41"
CALENDAR_ID = "calendar.pireva_avfallsschema_sundsgatan_41"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Aktivera custom integrations i alla tester."""
    yield


@pytest.fixture
def schedule():
    """Ett tomningsschema relativt dagens datum."""
    today = dt_util.now().date()
    return [
        {"date": (today - timedelta(days=2)).isoformat(), "waste_type": "Restavfall"},
        {"date": (today + timedelta(days=1)).isoformat(), "waste_type": "Matavfall"},
        {"date": (today + timedelta(days=8)).isoformat(), "waste_type": "Restavfall"},
        {"date": (today + timedelta(days=8)).isoformat(), "waste_type": "Matavfall"},
    ]


@pytest.fixture
def config_entry():
    """En config entry för testadressen."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={CONF_ADDRESS: ADDRESS, CONF_NUMBER: NUMBER},
        unique_id=UNIQUE_ID,
    )
