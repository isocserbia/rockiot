import datetime
import sys
import json
import logging
import threading
from urllib.parse import quote_plus

from pyrabbit2 import api
from django.conf import settings
from requests import HTTPError

from app.rabbitops import rabbit_events
from app.models import Device, LagDiffTemperature, LagDiffNO2, LagDiffSO2, LagDiffHumidity, LagDiffPM10, LagDiffPM25, \
    DeviceConnection
from app.rabbitops.rabbit_paho_publisher import PahoPublisher
from app.rabbitops.rabbit_task import RabbitTask
from app.rabbitops.rabbit_task_producer import RabbitTaskProducer

config = settings.BROKER_CONFIG

logger = logging.getLogger(__name__)


class RabbitOps:

    __lock = threading.Lock()

    client = api.Client(config['BROKER_HOST'] + ":" + config['BROKER_MNGMT_PORT'],
                        config['RABBITMNGMT_USER'], config['RABBITMNGMT_PASS'])

    paho_publisher = PahoPublisher()

    @classmethod
    def check_connection(cls, task: RabbitTask):
        try:
            logger.info("checking system health")
            alive = RabbitOps.client.is_alive(quote_plus(config['BROKER_VHOST']))
            healthy = RabbitOps._check_health_internally()
            logger.info("system health [alive: %s] [healthy: %s]" % (alive, healthy))
        except Exception as ex:
            logger.exception("Unknown exception during connection check", str(ex))
        RabbitTaskProducer.publish_delayed_task(RabbitTask("check_connection", 0))

    @classmethod
    def list_connections(cls, task: RabbitTask):
        logger.info("checking all devices connections")
        with cls.__lock:
            try:
                connection_map = {}
                connections = RabbitOps.client.get_connections()
                for c in connections:
                    c_user = c["user"]
                    connection_map[c_user] = c
                devices = Device.objects.all()
                for device in devices:
                    device_connection = DeviceConnection.objects.filter(device=device).last()
                    c = connection_map.get(device.device_id)
                    if not device_connection:
                        if c:
                            device_connection = DeviceConnection()
                            device_connection.device = device
                            device_connection.update_from_rabbitmq_connection(c)
                            device_connection.save()
                            logger.info("%s connection created" % device.device_id)
                    else:
                        if c:
                            if device_connection.client_id == c["variable_map"]["client_id"]:
                                device_connection.update_from_rabbitmq_connection(c)
                                device_connection.save()
                                logger.info("%s connection updated" % device.device_id)
                            else:
                                device_connection.state = "TERMINATED"
                                device_connection.terminated_at = datetime.datetime.now()
                                device_connection.save()
                                logger.info("%s connection terminated" % device.device_id)
                                device_connection = DeviceConnection()
                                device_connection.device = device
                                device_connection.update_from_rabbitmq_connection(c)
                                device_connection.save()
                                logger.info("%s connection created" % device.device_id)
                        else:
                            device_connection.state = "TERMINATED"
                            device_connection.terminated_at = datetime.datetime.now()
                            device_connection.save()
                            logger.info("%s connection terminated" % device.device_id)
            except Exception as ex:
                logger.exception("Unknown exception during device connections check", ex)

        RabbitTaskProducer.publish_delayed_task(RabbitTask("list_connections", 0))

    @classmethod
    def get_overview(cls, task: RabbitTask):
        logger.info("getting overview")
        overview = RabbitOps.client.get_overview()
        logger.info("overview " + str(overview))
        for o in overview:
            logger.info("overview " + str(o))

    @classmethod
    def check_devices_health(cls, task: RabbitTask):
        logger.info("checking devices health")
        try:
            cls.add_measurement_fault(LagDiffTemperature.objects.all(), 'temperature', 100)
            cls.add_measurement_fault(LagDiffHumidity.objects.all(), 'humidity', 100)
            cls.add_measurement_fault(LagDiffNO2.objects.all(), 'NO2', 100)
            cls.add_measurement_fault(LagDiffSO2.objects.all(), 'SO2', 100)
            cls.add_measurement_fault(LagDiffPM10.objects.all(), 'PM10', 100)
            cls.add_measurement_fault(LagDiffPM25.objects.all(), 'PM25', 100)
        except Exception as ex:
            logger.exception("Unknown exception during device health check", str(ex))
        RabbitTaskProducer.publish_delayed_task(RabbitTask("check_devices_health", 0))

    @classmethod
    def add_measurement_fault(cls, diffs, name='', threshold=5):
        for i, diff in enumerate(diffs):
            if diff.diff_perc and diff.diff_perc is not None and diff.diff_perc > threshold:
                device = Device.objects.get(device_id=diff.device_id)
                if 'faults' not in device.metadata:
                    device.metadata['faults'] = {}
                if name not in device.metadata['faults']:
                    device.metadata['faults'][name] = {}
                if str(diff.time) not in device.metadata['faults'][name]:
                    device.metadata['faults'][name][str(diff.time)] = \
                        ("%s diff too big [diff: %s]" % (name, diff.diff_perc))
                    device.save()
                    logger.warning("device %s fault saved [device_id: %s]" % (name, device.device_id))

    @classmethod
    def register_device(cls, task: RabbitTask):
        logger.info("Registering device [device-id: %s]" % task.correlation_id)
        try:
            RabbitOps._register_device_internal(task.correlation_id)
        except ValueError as ve:
            logger.error("Error executing task", str(ve))
        except:
            logger.error("Error executing task", sys.exc_info())

    @classmethod
    def activate_device(cls, task: RabbitTask):
        logger.info("Activating device [device-id: %s]" % task.correlation_id)
        try:
            RabbitOps._activate_device_internal(task.correlation_id)
        except ValueError as ve:
            logger.error("Error executing task", str(ve))
        except:
            logger.error("Error executing task", sys.exc_info())

    @classmethod
    def handle_activation_request(cls, task: RabbitTask):
        logger.info("Handling activation request [device-id: %s]" % task.correlation_id)
        try:
            device = Device.objects.get(device_id=task.correlation_id)
            if not device:
                raise ValueError("Device not found [device-id: %s]" % task.correlation_id)
            # if device.can_activate_from_device():
            RabbitOps._activate_device_internal(task.correlation_id)
            # else:
            #     raise ValueError("Device is faulty, can't be activated [device-id: %s]" % task.correlation_id)
        except ValueError as ve:
            logger.error("Error executing task", str(ve))
        except:
            logger.error("Error executing task", sys.exc_info())

    @classmethod
    def deactivate_device(cls, task: RabbitTask):
        logger.info("Deactivating device [device-id: %s]" % task.correlation_id)
        try:
            RabbitOps._deactivate_device_internal(task.correlation_id)
        except ValueError as ve:
            logger.error("Error executing task", str(ve))
        except RuntimeError as re:
            logger.error("Error executing task", re)

    @classmethod
    def terminate_device(cls, task: RabbitTask):
        logger.info("Terminating device [device-id: %s]" % task.correlation_id)
        try:
            RabbitOps._deactivate_device_internal(task.correlation_id, Device.TERMINATED)
        except ValueError as ve:
            logger.error("Error executing task", str(ve))
        except RuntimeError as re:
            logger.error("Error executing task", re)

    @classmethod
    def _register_device_internal(cls, device_id):

        device = Device.objects.get(device_id=device_id)
        if not device:
            raise ValueError("Device not found [device-id: %s]" % device_id)

        if not device.can_register():
            logger.warning("Device already exists [device-id: %s] [status: %s]" % (device_id, device.status))
            return

        vname = config['BROKER_VHOST']
        exchange = config['BROKER_EXCHANGE']
        device_pass = device.device_pass
        device_key = device.device_key

        try:
            if isinstance(RabbitOps.client.create_user(device_id, device_pass, None, "device"), Exception):
                raise ValueError("Device ingest user not created [device-id: %s]" % device_id)

            logger.info("Device ingest user created [device-id: %s]" % device_id)

            if isinstance(RabbitOps.client.set_vhost_permissions(vname, device_id, ".*", ".*", ".*"), Exception):
                raise ValueError("Failed setting vhost permissions [device-id: %s]" % device_id)

            body = json.dumps({
                "vhost": vname,
                "exchange": exchange,
                "write": config["BROKER_DEVICE_ACTIONS_TOPIC"],
                "read": ("(" + config["BROKER_ATTRIBUTES_TOPIC"] + "|"
                         + (config["BROKER_DEVICE_EVENTS_TOPIC"] % device_key) + ")")
            })

            action = "/api/topic-permissions/%s/%s" % (quote_plus(vname), device_id)
            RabbitOps.client._call(action, 'PUT', body, api.Client.json_headers)
            logger.info("Device initial permissions configured [device-id: %s]" % device_id)

            device.status = Device.REGISTERED
            device.save()

            event = rabbit_events.DeviceStatusEvent.construct_status(Device.NEW, Device.REGISTERED, "Device registered")
            cls.paho_publisher.publish((config["BROKER_DEVICE_EVENTS_TOPIC"] % device_key), device_id, event.to_json())
            logger.info("Device ingest user registered [device-id: %s]" % device_id)
            return True

        except HTTPError as err:
            raise RuntimeError("Device ingest user not registered", err.args)

        except Exception as ex:
            raise RuntimeError("Device ingest user not registered", ex.args)

    @classmethod
    def _activate_device_internal(cls, device_id):

        device = Device.objects.get(device_id=device_id)
        if not device:
            raise ValueError("Device not found [device-id: %s]" % device_id)

        if not device.can_activate():
            raise ValueError("Device can't be activated [device-id: %s] [status: %s]" % (device_id, device.status))

        vname = config['BROKER_VHOST']
        exchange = config['BROKER_EXCHANGE']
        device_key = device.device_key

        try:

            body = json.dumps({
                "vhost": vname,
                "exchange": exchange,
                "write": ("(" + config["BROKER_DEVICE_ACTIONS_TOPIC"] + "|"
                          + (config["BROKER_DEVICE_INGEST_TOPIC"] % device_key) + ")"),
                "read": ("(" + config["BROKER_ATTRIBUTES_TOPIC"] + "|"
                         + (config["BROKER_DEVICE_EVENTS_TOPIC"] % device_key) + ")")
            })

            action = "/api/topic-permissions/%s/%s" % (quote_plus(vname), device_id)
            RabbitOps.client._call(action, 'PUT', body, api.Client.json_headers)
            logger.info("Device ingest user permission configured [device-id: %s]" % device_id)

            device.status = Device.ACTIVATED
            device.save()

            event = rabbit_events.DeviceStatusEvent.construct_activation(Device.REGISTERED, Device.ACTIVATED,
                                                                         device.educational_facility.id,
                                                                         "Device activated")
            cls.paho_publisher.publish((config["BROKER_DEVICE_EVENTS_TOPIC"] % device_key), device_id, event.to_json())
            logger.info("Device ingest user activated [device-id: %s]" % device_id)
            return True

        except HTTPError as err:
            raise RuntimeError("Device ingest user not activated", err.args)

        except Exception as ex:
            raise RuntimeError("Device ingest user not activated", ex.args)

    @classmethod
    def _deactivate_device_internal(cls, device_id, new_status: Device.DEACTIVATED):

        device = Device.objects.get(device_id=device_id)
        if not device:
            raise ValueError("Device not found [device-id: %s]" % device_id)

        if not device.can_deactivate():
            raise ValueError("Device can't be deactivated [device-id: %s] [status: %s]" % (device_id, device.status))

        vname = config['BROKER_VHOST']
        exchange = config['BROKER_EXCHANGE']

        try:
            if isinstance(RabbitOps.client.set_vhost_permissions(vname, device_id, "", "", ""), Exception):
                raise ValueError("Failed removing vhost permissions [device-id: %s]" % device_id)

            body = json.dumps({
                "vhost": vname,
                "exchange": exchange,
                "write": "",
                "read": ""
            })

            action = "/api/topic-permissions/%s/%s" % (quote_plus(vname), device_id)
            RabbitOps.client._call(action, 'PUT', body, api.Client.json_headers)
            logger.info("Device ingest permission removed [device-id: %s]" % device_id)

            connections = RabbitOps.client.get_connections()
            for c in connections:
                if "user" in c and c["user"] == device_id:
                    logger.info("Closing device connection [device: %s] [name: %s]" % (device_id, c["name"]))
                    if isinstance(RabbitOps.client.delete_connection(c["name"]), Exception):
                        logger.error("Failed closing device connection [device-id: %s] [name: %s]" %
                                     (device_id, c["name"]))

            device.status = new_status
            device.save()
            logger.info("Device ingest user %s [device-id: %s]" % (new_status, device_id))

            return True

        except HTTPError as err:
            raise RuntimeError("Device ingest user not " + new_status, err.args)

        except Exception as ex:
            raise RuntimeError("Device ingest user not " + new_status, ex.args)

    @classmethod
    def _check_health_internally(cls):
        try:
            resp = RabbitOps.client._call('/api/health/checks/alarms', 'GET')
            logger.info("Health checks alarms response: %s" % resp)

            resp = RabbitOps.client._call('/api/health/checks/local-alarms', 'GET')
            logger.info("Health checks local-alarms response: %s" % resp)
            return True

        except HTTPError as err:
            raise RuntimeError("Error getting health checks", err.args)

        except Exception as ex:
            raise RuntimeError("Error getting health checks", ex.args)


