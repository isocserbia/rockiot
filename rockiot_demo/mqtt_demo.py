#!/usr/bin/env python
import os
import ssl
import sys
import uuid
from datetime import datetime
from time import sleep

import paho.mqtt.client as paho

import mqtt_demo_readings
from mqtt_events import DeviceAction, DeviceStatusEvent

BROKER_HOST = os.getenv("BROKER_HOST", default='172.17.0.2')
BROKER_MQTT_PORT = int(os.getenv("BROKER_MQTT_PORT", default="1883"))
BROKER_MQTT_SSL_PORT = int(os.getenv("BROKER_MQTT_SSL_PORT", default="8883"))
BROKER_VHOST = os.getenv("BROKER_VHOST", default='/')

BROKER_ATTRIBUTES_TOPIC = os.getenv("BROKER_ATTRIBUTES_TOPIC", default='v1.attributes')
BROKER_DEVICE_ACTIONS_TOPIC = os.getenv("BROKER_DEVICE_ACTIONS_TOPIC", default='v1.devices.actions')
BROKER_DEVICE_EVENTS_TOPIC = os.getenv("BROKER_DEVICE_EVENTS_TOPIC", default='v1.devices.%s.events')
BROKER_DEVICE_INGEST_TOPIC = os.getenv("BROKER_DEVICE_INGEST_TOPIC", default='v1.devices.%s.actions.ingest')

DEVICE_ID = os.getenv("DEVICE_ID", default='device1')
DEVICE_KEY = os.getenv("DEVICE_KEY", default='4OrcNTFSZUrYX6NqP0P3lz')
DEVICE_PASS = os.getenv("DEVICE_PASS", default='device1pass')

DEMO_SLEEP_SECONDS = int(os.getenv("DEMO_SLEEP_SECONDS", default='5'))
DEMO_IS_SSL = bool(os.getenv("DEMO_IS_SSL", default='True'))


class MqttDemo:

    def __init__(self):
        self.connected = False
        self.activating = False
        self.activated = False
        self.schoolId = None
        self.clientid = paho.base62(uuid.uuid4().int, padding=22)
        self.identified = str(DEVICE_ID) + "/" + str(self.clientid)
        self.client = paho.Client(self.clientid)  # create client object
        if DEMO_IS_SSL:
            self.client.tls_set(ca_certs="certs/ca_certificate.pem", certfile="certs/client_certificate.pem",
                                keyfile="certs/client_key.pem", cert_reqs=ssl.CERT_REQUIRED,
                                tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
            self.client.tls_insecure_set(True)
        self.client.username_pw_set(username=DEVICE_ID, password=DEVICE_PASS)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.connect(BROKER_HOST, BROKER_MQTT_SSL_PORT if DEMO_IS_SSL else BROKER_MQTT_PORT, keepalive=60)
        self.client.loop_start()
        print(self.identified + " loop started")
        self.start_publishing_sensor_data()

    def try_to_reconnect(self):
        self.client.loop_stop()
        self.clientid = paho.base62(uuid.uuid4().int, padding=22)
        self.identified = str(DEVICE_ID) + "/" + str(self.clientid)
        self.client = paho.Client(self.clientid)  # create client object
        if DEMO_IS_SSL:
            self.client.tls_set(ca_certs="certs/ca_certificate.pem", certfile="certs/client_certificate.pem",
                                keyfile="certs/client_key.pem", cert_reqs=ssl.CERT_REQUIRED,
                                tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
            self.client.tls_insecure_set(True)
        self.client.username_pw_set(username=DEVICE_ID, password=DEVICE_PASS)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.connect(BROKER_HOST, BROKER_MQTT_SSL_PORT if DEMO_IS_SSL else BROKER_MQTT_PORT, keepalive=60)
        self.client.loop_start()
        print(self.identified + (" publisher %s loop re-started" % self.clientid))

    def on_connect(self, client, userdata, flags, rc):
        if rc is not 0:
            print(self.identified + " failed connecting with result: " + paho.connack_string(rc))
            if rc is 4 or rc is 5:
                print(self.identified + " waiting for device registration... ")
            else:
                print(self.identified + " fatal error detected. Stopping mqtt client.")
                self.client.loop_stop()
                exit(0)
        else:
            print(self.identified + " connected with result: " + paho.connack_string(rc))
            self.client.subscribe(BROKER_ATTRIBUTES_TOPIC)
            self.client.subscribe(BROKER_DEVICE_EVENTS_TOPIC % DEVICE_KEY)
            self.connected = True

    def on_disconnect(self, client, userdata, rc):
        try:
            print("%s disconnected with result: %s, userdata: %s" % (self.identified, paho.error_string(rc), userdata))
        except:
            print(self.identified + (" publisher failed stopping client loop [reason: %s]" % sys.exc_info()[0]))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print(self.identified + " subscribed to topic: " + str(mid))
        return True

    def on_message(self, client, userdata, message):
        payload_decode = message.payload.decode('utf-8')
        print(self.identified + " received: " + payload_decode)
        event = DeviceStatusEvent.from_json(payload_decode)
        if not event:
            print(self.identified + " can't parse mqtt event")
            return
        if event.type == 'activation':
            self.activated = True
            self.activating = False
            self.schoolId = event.school_id
            print(self.identified + " received activation event [data: %s]" % event)
            print(self.identified + " device activated [data: %s]" % event)
        elif event.type == 'status':
            print(self.identified + " received status event [data: %s]" % event)
        else:
            print(self.identified + " received unknown event [data: %s]" % event)
        return True

    def publish_sensor_data(self):
        if self.client.is_connected():
            message = mqtt_demo_readings.random_sensor_data(DEVICE_ID, self.clientid, self.schoolId)
            topic = (BROKER_DEVICE_INGEST_TOPIC % DEVICE_KEY)
            self.client.publish(topic=topic, payload=message)
            print("%s sensor data sent to topic %s: %s" % (self.identified, topic, message))
        else:
            print("%s client disconnected" % self.identified)
            sys.exit(0)

    def publish_activate_action(self):
        message = DeviceAction("activation_request", self.clientid, DEVICE_ID, datetime.now().isoformat()).to_json()
        self.client.publish(topic=BROKER_DEVICE_ACTIONS_TOPIC, payload=message)
        print("%s activate_request sent to topic %s: %s" % (self.identified, BROKER_DEVICE_ACTIONS_TOPIC, message))
        self.activating = True

    def start_publishing_sensor_data(self):
        max_attempts_counter = 0
        while 1 == 1:
            if max_attempts_counter >= 200:
                print(self.identified + " failed to connect/activate (reached max attempts).")
                break
            sleep(DEMO_SLEEP_SECONDS)
            if self.connected:
                if self.activated:
                    self.publish_sensor_data()
                else:
                    max_attempts_counter = max_attempts_counter + 1
                    if self.activating:
                        print(self.identified + " waiting for activation...")
                    else:
                        sleep(DEMO_SLEEP_SECONDS)
                        self.publish_activate_action()
            else:
                max_attempts_counter = max_attempts_counter + 1
                if (max_attempts_counter % 10) == 0:
                    try:
                        print("%s trying to reconnect ..." % self.identified)
                        self.try_to_reconnect()
                    except:
                        print("%s can't reconnect %s" % (self.identified, sys.exc_info()))
                else:
                    print(self.identified + " waiting for connection...")


if __name__ == '__main__':
    try:
        MqttDemo()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
