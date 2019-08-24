import paho.mqtt.client as mqtt
import logging
import requests
import json
import random
import string
from homeassistant.helpers.entity import Entity
from .id_maker import IdMaker


API_URL_SESSION = "https://web-api-prod-obo.horizon.tv/oesp/v3/NL/nld/web/session"
API_URL_TOKEN = "https://web-api-prod-obo.horizon.tv/oesp/v3/NL/nld/web/tokens/jwt"
DEFAULT_HOST = "obomsg.prod.nl.horizon.tv"
DEFAULT_PORT = 443

_LOGGER = logging.getLogger(__name__)


class ZiggoClient(Entity):
    def __init__(self, username, password, on_message_callback):
        self.__username = username
        self.__password = password
        self.__retrieveSessionAndToken()
        self.__createMqttClient()
        self.__on_message_callback = on_message_callback

    def __createMqttClient(self):
        self.mqtt_clientId = IdMaker.make(30)
        _LOGGER.debug("ClientId: " + self.mqtt_clientId)
        self.__mqtt_client = mqtt.Client(
            client_id=self.mqtt_clientId, transport="websockets"
        )
        self.__mqtt_client.user_data_set(
            {"clientId": self.mqtt_clientId, "householdId": self.householdId}
        )
        self.__mqtt_client.username_pw_set(self.householdId, self.__jwToken)
        self.__mqtt_client.tls_set()
        # self.__mqtt_client.enable_logger(_LOGGER)
        # Register events.
        self.__mqtt_client.on_connect = self.__on_connect
        self.__mqtt_client.on_message = self.__on_message
        # self._mqtt_client.on_publish = self.__on_publish
        self.__mqtt_client.on_disconnect = self.__on_disconnect
        self.__mqtt_client.connect(DEFAULT_HOST, DEFAULT_PORT)
        self.__mqtt_client.loop_start()

    def subscribe(self, topic):
        self.__mqtt_client.subscribe(self.householdId + topic)

    def publish(self, topic, payload):
        topic = self.householdId + topic
        _LOGGER.debug("Publishing message:")
        _LOGGER.debug("  topic: " + topic)
        _LOGGER.debug("  payload: " + str(payload))
        self.__mqtt_client.publish(topic, payload)

    def __on_connect(self, client, userdata, flags, resultCode):
        if resultCode == 0:
            # Connection was successful.
            _LOGGER.debug("Connected to mqtt client.")
            self.isConnected = True
            self.subscribe("/+/status")

        elif resultCode == 5:
            # Connection refused - not authorised.
            # This can occur if the current connection expires, so refresh the credentials and try again.
            self.retrieveSessionAndToken()
            self.__mqtt_client.username_pw_set(self._householdId, self._jwToken)
            self.__mqtt_client.connect(DEFAULT_HOST, DEFAULT_PORT)
            self.__mqtt_client.loop_start()

        else:
            _LOGGER.error("Could not establish a MQTT connection with the device.")

    def __on_message(self, client, userdata, message):
        _LOGGER.debug("Mqtt message received:")
        _LOGGER.debug("  topic: " + message.topic)
        _LOGGER.debug("  payload: " + str(message.payload))
        self.__on_message_callback(client, userdata, message)

    def __on_disconnect(self, client, userdata, resultCode):
        _LOGGER.debug("Disconnected...")
        self.isConnected = False

    def __retrieveSessionAndToken(self):
        self.__session = self.__getSession(self.__username, self.__password)
        _LOGGER.debug(self.__session["customer"])
        self.householdId = self.__session["customer"]["householdId"]
        oespToken = self.__session["oespToken"]
        self.__jwToken = self.__getJwToken(oespToken, self.__username)

    def __getSession(self, username, password):
        payload = {"username": self.__username, "password": self.__password}
        r = requests.post(API_URL_SESSION, json=payload)

        if r.status_code == 200:
            session = r.json()
            # _LOGGER.debug("Retrieved session: " + str(session))
            _LOGGER.debug("Session retrieved")
            return session

        else:
            _LOGGER.error("Error retrieving session: " + str(r.status_code))
            _LOGGER.error("- Result headers: " + str(r.headers))
            _LOGGER.error("- Result body: " + str(r.content))
            return ""

    def __getJwToken(self, oespToken, username):
        _LOGGER.info("Retrieving JWT token")
        headers = {"X-OESP-Token": oespToken, "X-OESP-Username": username}
        r = requests.get(API_URL_TOKEN, headers=headers)

        if r.status_code == 200:
            jwtToken = r.json()
            _LOGGER.debug("Retrieved JWT token: " + str(jwtToken))
            return jwtToken["token"]
        else:
            _LOGGER.error("Error retrieving JWT token: " + str(r.status_code))
            _LOGGER.error("- Result headers: " + str(r.headers))
            _LOGGER.error("- Result body: " + str(r.content))
            return ""

