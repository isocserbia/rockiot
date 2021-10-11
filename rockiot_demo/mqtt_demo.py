#!/usr/bin/env python
import logging
import os
import ssl
import sys
import uuid
from datetime import datetime
from time import sleep

import paho.mqtt.client as paho

import mqtt_demo_readings
from mqtt_events import DeviceAction, DeviceEvent, PlatformEvent

BROKER_HOST = os.getenv("BROKER_HOST", default='localhost')
BROKER_MQTT_PORT = int(os.getenv("BROKER_MQTT_PORT", default="1883"))
BROKER_MQTT_SSL_PORT = int(os.getenv("BROKER_MQTT_SSL_PORT", default="8883"))
BROKER_VHOST = os.getenv("BROKER_VHOST", default='/')

BROKER_ATTRIBUTES_TOPIC = os.getenv("BROKER_ATTRIBUTES_TOPIC", default='v1.attributes')
BROKER_DEVICE_ACTIONS_TOPIC = os.getenv("BROKER_DEVICE_ACTIONS_TOPIC", default='v1.devices.actions')
BROKER_DEVICE_EVENTS_TOPIC = os.getenv("BROKER_DEVICE_EVENTS_TOPIC", default='v1.devices.%s.events')
BROKER_DEVICE_INGEST_TOPIC = os.getenv("BROKER_DEVICE_INGEST_TOPIC", default='v1.devices.%s.actions.ingest')

DEVICE_ID = os.getenv("DEVICE_ID", default='device1')
DEVICE_PASS = os.getenv("DEVICE_PASS", default='device1pass')

DEMO_SLEEP_SECONDS = int(os.getenv("DEMO_SLEEP_SECONDS", default='60'))
DEMO_IS_SSL = bool(os.getenv("DEMO_IS_SSL", default='False'))

LOG_FORMAT = '%(levelname)s %(asctime)s %(module)s %(name)s %(process)d %(thread)d %(message)s'
LOGGER = logging.getLogger(__name__)


class MqttDemo(object):
    """This is an example MQTT client that connects to the RockIOT platform
    and ingests demo sensor reading. Communication with platform is done
    via RabbitMQ using PUB/SUB actions/events.
    """

    def __init__(self):
        """Create a new instance of the MqttDemo class using parameters supplied via environment"""
        self.connected = False
        self.activating = False
        self.activated = False
        self.client_id = paho.base62(uuid.uuid4().int, padding=22)
        self.identified = f"{DEVICE_ID}/{self.client_id}"
        self.client = paho.Client(self.client_id)
        self.establish_connection()
        self.start_publishing_sensor_data()

    def establish_connection(self, set_ssl=True):
        """Configures MQTT client and establishes connection with the server"""
        if DEMO_IS_SSL and set_ssl:
            self.client.tls_set(ca_certs="/certs/ca_certificate.pem", certfile="/certs/client_certificate.pem",
                                keyfile="/certs/client_key.pem", cert_reqs=ssl.CERT_REQUIRED,
                                tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
            # skip verification of server hostname for now
            self.client.tls_insecure_set(True)

        self.client.username_pw_set(username=DEVICE_ID, password=DEVICE_PASS)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.connect(BROKER_HOST, BROKER_MQTT_SSL_PORT if DEMO_IS_SSL else BROKER_MQTT_PORT, keepalive=60)
        self.client.loop_start()
        LOGGER.info(self.identified + " loop started")

    def try_to_reconnect(self):
        """Attempts to reconnect by stopping the loop, establishing new connection and starting new event loop"""
        self.client.loop_stop()
        self.establish_connection(set_ssl=False)
        self.client.loop_start()
        LOGGER.warning(self.identified + (" publisher %s loop re-started" % self.client_id))

    def on_connect(self, client, userdata, flags, rc):
        """ On connect event callback @see paho.mqtt.Client
        This implementation subscribes to server topics in case of success,
        and logs failure reasons in case of unexpected server responses
        """
        if rc is 0:
            LOGGER.info(self.identified + " connected with result: " + paho.connack_string(rc))
            self.client.subscribe(BROKER_ATTRIBUTES_TOPIC)
            self.client.subscribe(BROKER_DEVICE_EVENTS_TOPIC % DEVICE_ID)
            self.publish_metadata_action()
            self.connected = True
        else:
            LOGGER.warning(self.identified + " failed connecting with result: " + paho.connack_string(rc))
            if rc is 4 or rc is 5:
                LOGGER.warning(self.identified + " waiting for device registration... ")
            else:
                LOGGER.critical(self.identified + " fatal error detected. Stopping mqtt client.")
                self.client.loop_stop()
                exit(0)

    def on_disconnect(self, client, userdata, rc):
        """ on_disconnect event callback @see paho.mqtt.Client
        This implementation simply logs that client disconnected from the platform
        """
        try:
            LOGGER.warning("%s disconnected with result: %s, userdata: %s" % (self.identified, paho.error_string(rc), userdata))
        except:
            LOGGER.warning(self.identified + (" publisher failed stopping client loop [reason: %s]" % sys.exc_info()[0]))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """ on_subscribe event callback @see paho.mqtt.Client.
        This implementation simply logs that subscription has been made
        """
        LOGGER.info(self.identified + " subscribed to topic: " + str(mid))
        return True

    def on_message(self, client, userdata, message):
        """ on_message event callback @see paho.mqtt.Client.
        In case of activation event, client starts ingesting data.
        Otherwise it simply logs the received event.
        """
        payload_decode = message.payload.decode('utf-8')
        LOGGER.info(f"{self.identified}: message on topic: {message.topic}")
        event = None
        try:
            event = DeviceEvent.from_json(payload_decode)
        except:
            try:
                event = PlatformEvent.from_json(payload_decode)
            except:
                LOGGER.debug(self.identified + " can parse mqtt event")
        if not event:
            LOGGER.error(self.identified + " unrecognized mqtt event")
            return
        if event.type == 'activation':
            self.activated = True
            self.activating = False
            LOGGER.info(self.identified + " received activation event [data: %s]" % event)
        elif event.type == 'status':
            LOGGER.info(self.identified + " received status event [data: %s]" % event)
        elif event.type == 'device_config':
            LOGGER.info(self.identified + " received device_config event [data: %s]" % event)
        elif event.type == 'device_metadata':
            LOGGER.info(self.identified + " received device_metadata event [data: %s]" % event)
        elif event.type == 'platform_attributes':
            LOGGER.info(self.identified + " received platform_attributes event [data: %s]" % event)
        else:
            LOGGER.warning(self.identified + " received unknown event [data: %s]" % event)
        return True

    def publish_sensor_data(self):
        """Publishes sensor data to ingest topic"""
        if self.client.is_connected():
            message = mqtt_demo_readings.random_sensor_data(self.client_id)
            topic = (BROKER_DEVICE_INGEST_TOPIC % DEVICE_ID)
            self.client.publish(topic=topic, payload=message)
            LOGGER.info("%s sensor data sent to topic %s: %s" % (self.identified, topic, message))
        else:
            LOGGER.critical("%s client disconnected" % self.identified)
            sys.exit(0)

    def publish_metadata_action(self):
        """Publishes device metadata to actions topic"""
        message = DeviceAction("device_metadata", self.client_id, DEVICE_ID, datetime.utcnow().isoformat(), {"key": "value"}).to_json()
        self.client.publish(topic=BROKER_DEVICE_ACTIONS_TOPIC, payload=message)
        LOGGER.info("%s device_metadata sent to topic %s: %s" % (self.identified, BROKER_DEVICE_ACTIONS_TOPIC, message))
        self.activating = True

    def publish_activate_action(self):
        """Publishes activation request to actions topic"""
        message = DeviceAction("activation_request", self.client_id, DEVICE_ID, datetime.utcnow().isoformat()).to_json()
        self.client.publish(topic=BROKER_DEVICE_ACTIONS_TOPIC, payload=message)
        LOGGER.info("%s activate_request sent to topic %s: %s" % (self.identified, BROKER_DEVICE_ACTIONS_TOPIC, message))
        self.activating = True

    def start_publishing_sensor_data(self):
        """Publishes sensor data in the loop for the demo purposes.
        It is important to check the status of connection and make actions only if connection is established.
        In case client is not activated, activation request will be sent.
        Once the client is connected and activated, sensor data are sent in the loop.
        """
        max_attempts_counter = 0
        while 1 == 1:
            if max_attempts_counter >= 200:
                LOGGER.critical(self.identified + " failed to connect/activate (reached max attempts).")
                break
            sleep(DEMO_SLEEP_SECONDS)
            if self.connected:
                if self.activated:
                    self.publish_sensor_data()
                else:
                    max_attempts_counter = max_attempts_counter + 1
                    if self.activating:
                        LOGGER.info(self.identified + " waiting for activation...")
                    else:
                        sleep(DEMO_SLEEP_SECONDS)
                        self.publish_activate_action()
            else:
                max_attempts_counter = max_attempts_counter + 1
                if (max_attempts_counter % 10) == 0:
                    try:
                        LOGGER.info("%s trying to reconnect ..." % self.identified)
                        self.try_to_reconnect()
                    except:
                        LOGGER.warning("%s can't reconnect %s" % (self.identified, sys.exc_info()))
                else:
                    LOGGER.info(self.identified + " waiting for connection...")


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
        if len(sys.argv) > 2:
            DEVICE_ID = sys.argv[1]
            DEVICE_PASS = sys.argv[2]
            print(f"DEVICE ID {DEVICE_ID}    DEVICE PASS {DEVICE_PASS}")
        MqttDemo()

    except KeyboardInterrupt:
        LOGGER.warning('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
