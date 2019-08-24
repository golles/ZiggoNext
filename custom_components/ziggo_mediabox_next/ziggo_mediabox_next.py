import logging
import json
import random
from .id_maker import IdMaker
from homeassistant.components.media_player import MediaPlayerDevice
from homeassistant.const import (
    STATE_PLAYING,
    STATE_PAUSED,
    STATE_ON,
    STATE_IDLE,
    STATE_OFF,
    STATE_UNAVAILABLE,
)
from homeassistant.components.media_player.const import (
    MEDIA_TYPE_TVSHOW,
    SUPPORT_PLAY,
    SUPPORT_PAUSE,
    SUPPORT_PLAY_MEDIA,
    SUPPORT_STOP,
    SUPPORT_NEXT_TRACK,
    SUPPORT_PREVIOUS_TRACK,
    SUPPORT_SELECT_SOURCE,
    SUPPORT_TURN_ON,
    SUPPORT_TURN_OFF,
)

# List with available media keys.
MEDIA_KEY_POWER = "Power"
MEDIA_KEY_ENTER = "Enter"  # Not yet implemented
MEDIA_KEY_ESCAPE = "Escape"  # Not yet implemented

MEDIA_KEY_HELP = "Help"  # Not yet implemented
MEDIA_KEY_INFO = "Info"  # Not yet implemented
MEDIA_KEY_GUIDE = "Guide"  # Not yet implemented

MEDIA_KEY_CONTEXT_MENU = "ContextMenu"  # Not yet implemented
MEDIA_KEY_CHANNEL_UP = "ChannelUp"
MEDIA_KEY_CHANNEL_DOWN = "ChannelDown"

MEDIA_KEY_RECORD = "MediaRecord"  # Not yet implemented
MEDIA_KEY_PLAY_PAUSE = "MediaPlayPause"
MEDIA_KEY_STOP = "MediaStop"  # Not yet implemented
MEDIA_KEY_REWIND = "MediaRewind"  # Not yet implemented
MEDIA_KEY_FAST_FORWARD = "MediaFastForward"  # Not yet implemented

_LOGGER = logging.getLogger(__name__)


class ZiggoMediaboxNext(MediaPlayerDevice):
    def __init__(
        self,
        deviceId,
        state,
        channels,
        mqtt_clientId,
        publish_callback,
        update_channels_callback,
    ):
        self.__deviceId = deviceId
        self.__publish_callback = publish_callback
        self.__name = deviceId + ""
        self.__state = state
        self.__channels = channels
        self.__currentChannelId = None
        self.__update_channels_callback = update_channels_callback
        self.__mqtt_clientId = mqtt_clientId
        self.__channelImage = None
        self.__sourceType = None
        self.__playSpeed = 0

    def update(self):
        if self.__state == "ONLINE_RUNNING":
            self.__channels = self.__update_channels_callback()
            self.__channelImage = (
                self.__channels[self.__currentChannelId].streamImage
                + "?"
                + str(random.randrange(10000000))
            )
        _LOGGER.debug(self.state)

    def __publish(self, topic, payload):
        self.__publish_callback(topic, payload)

    @property
    def icon(self):
        """Return the icon of the player."""
        return "mdi:television-classic"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.__name

    def setState(self, state):
        self.__state = state

    @property
    def state(self):
        """Return the state of the player."""
        if self.__state == "ONLINE_RUNNING":
            if self.__playSpeed == 0:
                return STATE_PAUSED
            return STATE_PLAYING
        elif self.__state == "ONLINE_STANDBY":
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
            | SUPPORT_STOP
            | SUPPORT_PREVIOUS_TRACK
            | SUPPORT_NEXT_TRACK
            | SUPPORT_SELECT_SOURCE
            | SUPPORT_TURN_ON
            | SUPPORT_TURN_OFF
        )

    def handleStateMessage(self, statusJson):
        self.__currentChannelId = statusJson["playerState"]["source"]["channelId"]
        self.__sourceType = statusJson["playerState"]["sourceType"]
        self.__playSpeed = statusJson["playerState"]["speed"]
        _LOGGER.debug(self.__currentChannelId)
        _LOGGER.debug(self.__sourceType)
        _LOGGER.debug(self.__playSpeed)

    @property
    def available(self):
        """Return True if the device is available."""
        return self.state != STATE_UNAVAILABLE

    def turn_on(self):
        """Turn the media player on."""
        _LOGGER.debug("Turning the media player on.")
        self.__send_key(MEDIA_KEY_POWER)

    def turn_off(self):
        """Turn the media player off."""
        _LOGGER.info("Turning the media player off.")
        self.__send_key(MEDIA_KEY_POWER)

    @property
    def media_image_url(self):
        """Return the media image URL."""
        return self.__channelImage

    @property
    def media_title(self):
        """Return the media title."""
        if self.__currentChannelId:
            return self.__channels[self.__currentChannelId].title
        return None

    @property
    def source(self):
        """Name of the current channel."""
        if self.__currentChannelId:
            return self.__channels[self.__currentChannelId].title
        return None

    @property
    def source_list(self):
        if self.__channels == None:
            return None
        else:
            return [channel.title for channel in self.__channels.values()]

    def __send_key(self, key):
        payload = (
            '{"type":"CPE.KeyEvent","status":{"w3cKey":"'
            + key
            + '","eventType":"keyDownUp"}}'
        )

        self.__publish("/" + self.__deviceId, payload)

    def select_source(self, source):
        """Select the channel."""
        _LOGGER.info("Switching source to '" + source + "'")
        channel = [src for src in self.__channels.values() if src.title == source][0]
        _LOGGER.debug(str(channel))
        payload = (
            '{"id":"'
            + IdMaker.make(8)
            + '","type":"CPE.pushToTV","source":{"clientId":"'
            + self.__mqtt_clientId
            + '","friendlyDeviceName":"NodeJs"},"status":{"sourceType":"linear","source":{"channelId":"'
            + channel.serviceId
            + '"},"relativePosition":0,"speed":1}}'
        )

        self.__publish("/" + self.__deviceId, payload)
        self.__currentChannelId = channel.serviceId
        self.update()

    def media_play_pause(self):
        """Simulate play pause media player."""
        _LOGGER.info("Play/pause the media player.")

        self.__send_key(MEDIA_KEY_PLAY_PAUSE)

    def media_next_track(self):
        """Send next track command."""
        _LOGGER.info("Switching to the next channel.")

        self.__send_key(MEDIA_KEY_CHANNEL_UP)
        self.update()

    def media_previous_track(self):
        """Send previous track command."""
        _LOGGER.info("Switching to the previous channel.")
        self.__send_key(MEDIA_KEY_CHANNEL_DOWN)
        self.update()

    def media_play(self):
        self.__send_key(MEDIA_KEY_PLAY_PAUSE)
        self.update()

    def media_pause(self):
        self.__send_key(MEDIA_KEY_PLAY_PAUSE)
        self.update()
