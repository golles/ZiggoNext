"""The ziggo_mediabox_next component."""
import logging
from .const import ZIGGO_API
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD
)
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from ziggonext import ZiggoNext

DOMAIN = 'ziggonext'
_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string
    })
}, extra=vol.ALLOW_EXTRA,)

def setup(hass, config):
    """Your controller/hub specific code."""
    # Data that you want to share with your platforms
    api = ZiggoNext(config[DOMAIN][CONF_USERNAME], config[DOMAIN][CONF_PASSWORD])
    api.initialize(_LOGGER)
    hass.data[ZIGGO_API] = api
    hass.helpers.discovery.load_platform('media_player', DOMAIN, {}, config)
    hass.helpers.discovery.load_platform('sensor', DOMAIN, {}, config)
    return True