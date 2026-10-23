"""Fixtures for the Vson integration."""

# <!-- hass-standards:domain-fixtures:start -->
# Use pytest_homeassistant_custom_component.common.MockConfigEntry for
# mock_config_entry when the integration uses config entries.
# Define mock_client only when an external communication client is present.
# Mock external communication boundaries, never Home Assistant core modules.
# Keep integration-specific fixtures below this managed block.
# <!-- hass-standards:domain-fixtures:end -->

from unittest.mock import patch

import pytest
from blesession.testing import FakeClient, fake_connect
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.vson.vson_ble.const import SERVICE_WP6003, CHAR_CMD, CHAR_NOTI

ADDRESS = "AA:BB:CC:DD:EE:FF"
PACKET = bytes.fromhex("0a0001010e02010908000065000f01000251")


@pytest.fixture
def mock_config_entry(hass):
    entry = MockConfigEntry(
        domain="vson", title="WP6003 EEFF", unique_id=ADDRESS, data={}
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_client():
    client = FakeClient()
    client.add_characteristic(SERVICE_WP6003, CHAR_CMD)
    client.add_characteristic(SERVICE_WP6003, CHAR_NOTI)
    client.on_write = lambda _char, _data: client.reply(PACKET)
    with patch("blesession.session.establish_connection", fake_connect(client)):
        yield client
