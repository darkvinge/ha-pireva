"""Tester för API-klienten."""

import pytest

from custom_components.ha_pireva.api import build_url, normalize_address


@pytest.mark.parametrize(
    ("address", "expected"),
    [
        ("Sundsgatan", "sundsgatan"),
        ("Västra vägen", "vastra-vagen"),
        ("  Östra  Långgatan ", "ostra-langgatan"),
        ("Rue Café", "rue-cafe"),
    ],
)
def test_normalize_address(address, expected):
    assert normalize_address(address) == expected


def test_build_url():
    assert (
        build_url("Sundsgatan", " 41A ")
        == "https://www.pireva.se/tomningsschema/sundsgatan-41a/?output=json"
    )
