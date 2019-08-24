"""Support for interface with a Ziggo Mediabox Next."""
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.components.media_player import PLATFORM_SCHEMA
from .ziggo_next_container import ZiggoNextContainer
import time

_LOGGER = logging.getLogger(__name__)


# Validation of the user's configuration.
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_USERNAME): cv.string, vol.Required(CONF_PASSWORD): cv.string}
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    container = ZiggoNextContainer(config, add_entities)
    time.sleep(10)
    add_entities(container.players.values(), True)
