"""Support for interface with a Ziggo Mediabox Next."""
import logging
import random
from homeassistant.components.media_player import MediaPlayerDevice

from homeassistant.components.media_player.const import (
    MEDIA_TYPE_TVSHOW,
    SUPPORT_NEXT_TRACK,
    SUPPORT_PAUSE,
    SUPPORT_PLAY,
    SUPPORT_PREVIOUS_TRACK,
    SUPPORT_SELECT_SOURCE,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
)

from homeassistant.const import (
    STATE_OFF,
    STATE_PAUSED,
    STATE_PLAYING,
    STATE_UNAVAILABLE,
    CONF_USERNAME,
    CONF_PASSWORD
)

from ziggonext import (
	ZiggoNextBoxState,
	ZiggoNext,
    ONLINE_RUNNING,
    ONLINE_STANDBY
)
import time
DOMAIN = "ziggonext"

_LOGGER = logging.getLogger(__name__)
def setup_platform(hass, config, add_entities, discovery_info=None):
    players = []
    api = ZiggoNext(config[CONF_USERNAME], config[CONF_PASSWORD])
    api.initialize(_LOGGER)
    time.sleep(5)
    for box in api.settopBoxes.keys():
        players.append(ZiggoNextMediaPlayer(box, api))
    add_entities(players, True)

class ZiggoNextMediaPlayer(MediaPlayerDevice):
    """The home assistant media player"""

    boxState: ZiggoNextBoxState

    def __init__(self, boxId: str, api: ZiggoNext):
        """Init the media player"""
        self.api = api
        self.box_id = boxId
        self.box_state = None

    def update(self):
        """Updating the box"""
        self.api.load_channels()
        self.box_state = self.api.get_settop_box_state(self.box_id)
        _LOGGER.debug(self.box_state.image)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.box_id

    @property
    def state(self):
        """Return the state of the player."""
        if self.box_state is None:
            return STATE_UNAVAILABLE
        elif self.box_state.state == ONLINE_RUNNING:
            if self.box_state.paused:
                return STATE_PAUSED
            return STATE_PLAYING
        elif self.box_state.state == ONLINE_STANDBY:
            return STATE_OFF
        return STATE_UNAVAILABLE

    @property
    def media_content_type(self):
        """Return the media type."""
        return MEDIA_TYPE_TVSHOW

    @property
    def supported_features(self):
        return (
            SUPPORT_PLAY
            | SUPPORT_PAUSE
            | SUPPORT_TURN_ON
            | SUPPORT_TURN_OFF
            | SUPPORT_SELECT_SOURCE
            | SUPPORT_NEXT_TRACK
            | SUPPORT_PREVIOUS_TRACK
        )

    @property
    def available(self):
        """Return True if the device is available."""
        return self.api.is_available(self.box_id)

    def turn_on(self):
        """Turn the media player on."""
        self.api.turn_on(self.box_id)

    def turn_off(self):
        """Turn the media player off."""
        self.api.turn_off(self.box_id)

    @property
    def media_image_url(self):
        """Return the media image URL."""
        if self.box_state.image is not None:
            return self.box_state.image + "?" + str(random.randrange(1000000))
        return None

    @property
    def media_title(self):
        """Return the media title."""
        return self.box_state.title

    @property
    def source(self):
        """Name of the current channel."""
        return self.box_state.channelTitle

    @property
    def source_list(self):
        return [channel.title for channel in self.api.channels.values()]

    def select_source(self, source):
        self.api.select_source(source, self.box_id)

    def media_play(self):
        self.api.play(self.box_id)

    def media_pause(self):
        self.api.pause(self.box_id)

    def media_next_track(self):
        """Send next track command."""
        self.api.next_channel(self.box_id)

    def media_previous_track(self):
        """Send previous track command."""
        self.api.previous_channel(self.box_id)
