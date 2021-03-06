import logging
import sys
import uuid
from time import sleep

import paho.mqtt.client as paho
from django.conf import settings

from app.core.singleton import Singleton

config = settings.BROKER_CONFIG

BROKER_HOST = config["BROKER_HOST"]
BROKER_MQTT_PORT = int(config["BROKER_MQTT_PORT"])
BROKER_VHOST = config["BROKER_VHOST"]
MQTTEVENTPRODUCER_USER = config["MQTTEVENTPRODUCER_USER"]
MQTTEVENTPRODUCER_PASS = config["MQTTEVENTPRODUCER_PASS"]

logger = logging.getLogger(__name__)


@Singleton
class PahoPublisher:

    def __init__(self):
        self.conflag = False
        self.initialized = False
        self.clientid = paho.base62(uuid.uuid4().int, padding=22)
        self.client = paho.Client(self.clientid)  # create client object
        self.client.username_pw_set(username=MQTTEVENTPRODUCER_USER, password=MQTTEVENTPRODUCER_PASS)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

    def start(self):
        self.client.connect(BROKER_HOST, BROKER_MQTT_PORT, keepalive=60)
        self.client.loop_start()
        self.initialized = True
        logger.info("Paho publisher %s loop started" % self.clientid)

    def on_disconnect(self, client, userdata, rc):
        try:
            logger.warning("Paho publisher %s disconnected [rc: %s]" % (self.clientid, rc))
            if rc == paho.MQTT_ERR_CONN_LOST or rc == paho.MQTT_ERR_NO_CONN:
                logger.warning("Paho publisher %s is re-connecting [rc: %]" % (self.clientid, paho.error_string(rc)))
                self.client.reconnect()
        except:
            logger.warning("Paho publisher %s failed stopping client loop [reason: %s]" % (self.clientid, sys.exc_info()[0]))

    def on_connect(self, client, userdata, flags, rc):
        self.conflag = True
        logger.info("Paho publisher %s connected with result: %s" % (self.clientid, str(rc)))

    def publish(self, topic, device, message):
        if not self.initialized:
            self.start()
        while 1 == 1:
            if not self.conflag:
                logger.info("Paho publisher %s waiting for connection..." % self.clientid)
                sleep(5)
            else:
                message_info = self.client.publish(topic=topic, payload=message, qos=2)
                logger.info("Paho publisher %s Awaiting ACK [device-id: %s] [message-id: %s]" % (self.clientid, device, message_info.mid))
                message_info.wait_for_publish()
                logger.info("Paho publisher %s Received ACK [device-id: %s] [message-id: %s]" % (self.clientid, device, message_info.mid))
                return
