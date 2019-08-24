# from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from .ziggo_client import ZiggoClient
from .ziggo_mediabox_next import ZiggoMediaboxNext
from .ziggo_channel import ZiggoChannel
from .id_maker import IdMaker
import logging
import json
import requests

_LOGGER = logging.getLogger(__name__)
API_URL_CHANNELS = "https://web-api-prod-obo.horizon.tv/oesp/v3/NL/nld/web/channels"


class ZiggoNextContainer:
    def __init__(self, config, add_entities):
        self.__add_entities = add_entities
        self.__ziggoClient = ZiggoClient(
            config[CONF_USERNAME], config[CONF_PASSWORD], self.__on_message
        )
        self.players = {}
        self.channels = {}
        self.__get_channels()

    def __createSettopBox(self, deviceId, state):
        box = ZiggoMediaboxNext(
            deviceId,
            state,
            self.channels,
            self.__ziggoClient.mqtt_clientId,
            self.__ziggoClient.publish,
            self.__get_channels,
        )
        self.players[deviceId] = box

    def __on_message(self, client, userdata, message):
        payload = json.loads(message.payload.decode("utf-8"))
        _LOGGER.debug(str(payload))
        if ("deviceType" in payload) and (payload["deviceType"] == "STB"):
            deviceId = payload["source"]
            state = payload["state"]
            if not deviceId in self.players.keys():
                self.__createSettopBox(deviceId, state)
                self.__ziggoClient.publish(
                    "/" + deviceId,
                    '{"id":"'
                    + IdMaker.make(8)
                    + '","type":"CPE.getUiStatus","source":"'
                    + self.__ziggoClient.mqtt_clientId
                    + '"}',
                )
                self.__ziggoClient.subscribe("/" + self.__ziggoClient.mqtt_clientId)
                self.__ziggoClient.subscribe("/" + deviceId)
                self.__ziggoClient.subscribe("/" + deviceId + "/status")
                self.__ziggoClient.subscribe("")
                _LOGGER.debug("New settopbox added: " + deviceId)
            self.players[deviceId].setState(state)
        if "status" in payload:
            deviceId = payload["source"]
            self.players[deviceId].handleStateMessage(payload["status"])

    def __get_channels(self):
        _LOGGER.debug("Retrieving channels...")
        r = requests.get(API_URL_CHANNELS)
        if r.status_code == 200:
            content = r.json()
            for channel in content["channels"]:
                station = channel["stationSchedules"][0]["station"]
                serviceId = station["serviceId"]
                self.channels[serviceId] = ZiggoChannel(
                    channel["channelNumber"],
                    serviceId,
                    channel["title"],
                    station["images"][0]["url"],
                    station["images"][2]["url"],
                )
            return self.channels
        else:
            _LOGGER.error("Error retrieving channels: " + str(r.status_code))
            _LOGGER.error("- Result headers: " + str(r.headers))
            _LOGGER.error("- Result body: " + str(r.content))
