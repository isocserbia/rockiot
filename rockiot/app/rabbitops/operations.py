import datetime
import json
import logging

from urllib.parse import quote_plus

from django.conf import settings
from django.db import IntegrityError
from django.db.models import Q
from pyrabbit2 import api
from requests import HTTPError
from simple_history.utils import update_change_reason

from app.models import Device, DeviceConnection, PlatformAttribute
from app.rabbitops import actions_events
from app.rabbitops.mqtt_publisher import PahoPublisher
from statsd import StatsClient

config = settings.BROKER_CONFIG

logger = logging.getLogger(__name__)


statsd = StatsClient(host='statsd',
                     port=9125,
                     prefix=None,
                     maxudpsize=512,
                     ipv6=False)


def get_mngmt_client():
    return api.Client(config['BROKER_HOST'] + ":" + config['BROKER_MNGMT_PORT'],
                      config['RABBITMNGMT_USER'], config['RABBITMNGMT_PASS'])


def check_system_health():
    responses = {}
    logger.debug("checking system health")
    try:
        client = get_mngmt_client()
        resp_alarms = client._call('/api/health/checks/alarms', 'GET')
        responses["alarms"] = resp_alarms
        logger.info("Health checks alarms response: %s" % resp_alarms)
        resp_alarms_local = client._call('/api/health/checks/local-alarms', 'GET')
        responses["alarms_local"] = resp_alarms_local
        logger.info("Health checks local-alarms response: %s" % resp_alarms_local)
        return json.dumps(responses)
    except Exception as ex:
        logger.exception("Unknown exception during connection check", exc_info=ex)
        return json.dump({})


def get_overview():
    logger.debug("getting overview")
    overview = get_mngmt_client().get_overview()
    logger.info("overview " + str(overview))
    return json.dumps(overview)


def update_connections():
    logger.debug("updating connections")
    connection_map = {}
    connections = RabbitOps.client.get_connections()
    for c in connections:
        c_user = c["user"]
        c_client = c.get("variable_map", {}).get("client_id")
        if not c_client or c_client is None or "mqtteventproducer" == c_user:
            continue
        connection_map[c_user] = {}
        connection_map[c_user][c_client] = c
        logger.debug(f"Found {c_user} active connection ...")

    dcs = DeviceConnection.objects.filter(Q(state='UNKNOWN') | Q(state='RUNNING')).prefetch_related('device')
    for dc in dcs:
        try:
            device = dc.device
            logger.debug(f"Found {device.device_id} connection in db ...")
            conn = connection_map.get(device.device_id)
            if conn or conn is not None:
                dconn = conn.get(dc.client_id, None)
                if dconn is not None:
                    try:
                        dc.update_from_rabbitmq_connection(dconn)
                        dc.save()
                        logger.info(f"{device.device_id} connection updated")
                        statsd.gauge(f'rockiot.connected.{device.device_id}', 1)
                    except:
                        dcs_existing = DeviceConnection.objects.filter(name=dconn["name"], client_id=dconn["client_id"])
                        dcs_existing.update_from_rabbitmq_connection(dconn)
                        dcs_existing.save()
                        logger.info(f"{device.device_id} connection updated")
                        statsd.gauge(f'rockiot.connected.{device.device_id}', 1)
                else:
                    dc.state = Device.TERMINATED
                    dc.terminated_at = datetime.datetime.utcnow()
                    dc.save()
                    logger.info("%s connection changed, terminating ... " % device.device_id)
                    statsd.incr(f'rockiot.connection.terminated.{device.device_id}')
                    statsd.gauge(f'rockiot.connected.{device.device_id}', 0)
                    new_dc = DeviceConnection()
                    new_dc.device = dc.device
                    new_dc.update_from_rabbitmq_connection(list(conn.values())[0])
                    new_dc.save()
                    logger.info("%s new connection created" % device.device_id)
                    statsd.gauge(f'rockiot.connected.{device.device_id}', 1)
                del connection_map[device.device_id]
            else:
                dc.state = Device.TERMINATED
                dc.terminated_at = datetime.datetime.utcnow()
                dc.save()
                logger.info("%s connection terminated" % device.device_id)
                statsd.incr(f'rockiot.connection.terminated.{device.device_id}')
                statsd.gauge(f'rockiot.connected.{device.device_id}', 0)
        except:
            logger.error(f"Error updating device connection [device: {device.device_id}]", exc_info=True)

    for did in list(connection_map.keys()):
        for cid in list(connection_map[did].keys()):
            try:
                connection = connection_map[did][cid]
                name = connection["name"]
                client_id = connection["variable_map"]["client_id"]
                if not DeviceConnection.objects.filter(name=name, client_id=client_id).exists():
                    new_dc = DeviceConnection()
                    new_dc.device = Device.objects.get(device_id=did)
                    new_dc.update_from_rabbitmq_connection(connection)
                    new_dc.save()
                    logger.info(f"{did} new connection created [client: {cid}]")
                    statsd.gauge(f'rockiot.connected.{did}', 1)
                else:
                    logger.info(f"{did} skipped, connection already exists [client: {cid}]")
            except:
                logger.error("Error creating device connection", exc_info=True)
    return True


def register_device(did):
    logger.debug("Registering device [device-id: %s]" % did)
    try:
        return RabbitOps._register_device_internal(did)
    except ValueError as ve:
        logger.error("Error executing task: " + str(ve))
    except RuntimeError as re:
        logger.error("Error executing task", re)
    return False


def activate_device(did):
    logger.debug("Activating device [device-id: %s]" % did)
    try:
        return RabbitOps._activate_device_internal(did)
    except ValueError as ve:
        logger.error("Error executing task: ", exc_info=ve)
    except:
        logger.error("Error executing task", exc_info=True)
    return False


def handle_activation_request(did):
    logger.debug("Handling activation request [device-id: %s]" % did)
    try:
        device = Device.objects.get(device_id=did)
        if not device:
            raise ValueError("Device not found [device-id: %s]" % did)
        if device.can_activate_from_device():
            return RabbitOps._activate_device_internal(did, True)
        else:
            raise ValueError("Device can't be activated remotely[device-id: %s]" % did)
    except ValueError as ve:
        logger.error("Error executing task: ", exc_info=ve)
    except:
        logger.error("Error executing task", exc_info=True)
    return False


def deactivate_device(did):
    logger.debug("Deactivating device [device-id: %s]" % did)
    try:
        return RabbitOps._deactivate_device_internal(did)
    except ValueError as ve:
        logger.error("Error executing task: ", exc_info=ve)
    except:
        logger.error("Error executing task", exc_info=True)
    return False


def terminate_device(did):
    logger.debug("Terminating device [device-id: %s]" % did)
    try:
        return RabbitOps._deactivate_device_internal(did, Device.TERMINATED)
    except ValueError as ve:
        logger.error("Error executing task: ", exc_info=ve)
    except:
        logger.error("Error executing task", exc_info=True)
    return False


def send_device_event(did, event_type):
    logger.debug("Sending Device Event [device-id: %s] [type: %s]" % (did, event_type))
    try:
        return RabbitOps._send_device_event(did, event_type)
    except ValueError as ve:
        logger.error("Error executing task: ", exc_info=ve)
    except:
        logger.error("Error executing task", exc_info=True)
    return False


def save_device_metadata(did, metadata):
    logger.debug("Saving Device metadata [device-id: %s]" % did)
    try:
        device = Device.objects.get(device_id=did)
        if not device:
            raise ValueError("Device not found [device-id: %s]" % did)
        device.metadata = metadata
        device.save()
        update_change_reason(device, 'Metadata saved (by device)')
        statsd.gauge(f'rockiot.metadata.saved.{device.device_id}', datetime.datetime.now().timestamp())
        return True
    except ValueError as ve:
        logger.error("Error executing task: ", exc_info=ve)
    except:
        logger.error("Error executing task", exc_info=True)
    return False


def send_device_metadata(did):
    logger.debug("Sending Device metadata [device-id: %s]" % did)
    try:
        return RabbitOps._send_device_metadata_internal(did)
    except ValueError as ve:
        logger.error("Error executing task: ", exc_info=ve)
    except:
        logger.error("Error executing task", exc_info=True)
    return False


def send_platform_attributes():
    logger.debug("Sending Platform Attributes")
    try:
        return RabbitOps._send_platform_attributes_internal()
    except ValueError as ve:
        logger.error("Error executing task: ", exc_info=ve)
    except:
        logger.error("Error executing task", exc_info=True)
    return False


class RabbitOps:
    client = api.Client(config['BROKER_HOST'] + ":" + config['BROKER_MNGMT_PORT'],
                        config['RABBITMNGMT_USER'], config['RABBITMNGMT_PASS'])

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
                         + (config["BROKER_DEVICE_EVENTS_TOPIC"] % device_id) + ")")
            })

            action = "/api/topic-permissions/%s/%s" % (quote_plus(vname), device_id)
            RabbitOps.client._call(action, 'PUT', body, api.Client.json_headers)
            logger.info("Device initial permissions configured [device-id: %s]" % device_id)

            event = actions_events.DeviceEvent.construct_status(Device.NEW, Device.REGISTERED, "Device registered")
            PahoPublisher.Instance().publish((config["BROKER_DEVICE_EVENTS_TOPIC"] % device_id), device_id,
                                             event.to_json(allow_nan=False))
            logger.info("Device ingest user registered [device-id: %s]" % device_id)
            return True

        except HTTPError as err:
            device.status = Device.NEW
            device.save()
            raise RuntimeError("Device ingest user not registered", err.args)

        except Exception as ex:
            device.status = Device.NEW
            device.save()
            raise RuntimeError("Device ingest user not registered", ex.args)

    @classmethod
    def _activate_device_internal(cls, device_id, update_status=False):

        device = Device.objects.get(device_id=device_id)
        if not device:
            raise ValueError("Device not found [device-id: %s]" % device_id)

        if not device.can_activate():
            raise ValueError("Device can't be activated [device-id: %s] [status: %s]" % (device_id, device.status))

        vname = config['BROKER_VHOST']
        exchange = config['BROKER_EXCHANGE']

        try:

            body = json.dumps({
                "vhost": vname,
                "exchange": exchange,
                "write": ("(" + config["BROKER_DEVICE_ACTIONS_TOPIC"] + "|"
                          + (config["BROKER_DEVICE_INGEST_TOPIC"] % device_id) + ")"),
                "read": ("(" + config["BROKER_ATTRIBUTES_TOPIC"] + "|"
                         + (config["BROKER_DEVICE_EVENTS_TOPIC"] % device_id) + ")")
            })

            action = "/api/topic-permissions/%s/%s" % (quote_plus(vname), device_id)
            RabbitOps.client._call(action, 'PUT', body, api.Client.json_headers)
            logger.info("Device ingest user permission configured [device-id: %s]" % device_id)

            if update_status:
                device.status = Device.ACTIVATED
                device.save()
                update_change_reason(device, 'Status changed to: ACTIVATED (by device)')
                logger.info("Device status updated [device-id: %s] [status: %s]" % (device_id, Device.ACTIVATED))

            event = actions_events.DeviceEvent.construct_activation(Device.REGISTERED, Device.ACTIVATED,
                                                                   "Device activated")
            PahoPublisher.Instance().publish((config["BROKER_DEVICE_EVENTS_TOPIC"] % device_id), device_id,
                                             event.to_json(allow_nan=False))
            logger.info("Device ingest user activated [device-id: %s]" % device_id)
            return True

        except HTTPError as err:
            device.status = Device.REGISTERED
            device.save()
            update_change_reason(device, 'Device activation failed')
            raise RuntimeError("Device ingest user not activated", err.args)

        except Exception as ex:
            device.status = Device.REGISTERED
            device.save()
            raise RuntimeError("Device ingest user not activated", ex.args)

    @classmethod
    def _deactivate_device_internal(cls, device_id, new_status=Device.DEACTIVATED):

        device = Device.objects.get(device_id=device_id)
        current_status = device.status
        if not device:
            raise ValueError("Device not found [device-id: %s]" % device_id)

        if not device.can_deactivate():
            raise ValueError("Device can't be deactivated [device-id: %s] [status: %s]" % (device_id, device.status))

        vname = config['BROKER_VHOST']
        exchange = config['BROKER_EXCHANGE']

        try:
            # if isinstance(RabbitOps.client.set_vhost_permissions(vname, device_id, "", "", ""), Exception):
            #     raise ValueError("Failed removing vhost permissions [device-id: %s]" % device_id)

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

            logger.info("Device ingest user %s [device-id: %s]" % (new_status, device_id))
            return True

        except HTTPError as err:
            device.status = current_status
            device.save()
            raise RuntimeError("Device ingest user not " + new_status, err.args)

        except Exception as ex:
            device.status = current_status
            device.save()
            raise RuntimeError("Device ingest user not " + new_status, ex.args)

    @classmethod
    def _send_device_event(cls, device_id, event_type):

        device = Device.objects.get(device_id=device_id)
        if not device:
            raise ValueError("Device not found [device-id: %s]" % device_id)

        try:
            event = actions_events.DeviceEvent.construct_device_event(event_type)
            PahoPublisher.Instance().publish((config["BROKER_DEVICE_EVENTS_TOPIC"] % device_id), device_id,
                                             event.to_json(allow_nan=False))
            logger.info("Device Event sent [device-id: %s] [type: %s]" % (device_id, event_type))
            return True

        except HTTPError as err:
            raise RuntimeError("Device Event not sent", err.args)

        except Exception as ex:
            raise RuntimeError("Device Event not sent", ex.args)

    @classmethod
    def _send_device_metadata_internal(cls, device_id):

        device = Device.objects.get(device_id=device_id)
        if not device:
            raise ValueError("Device not found [device-id: %s]" % device_id)

        try:
            event = actions_events.DeviceEvent.construct_device_metadata_changed(device.metadata)
            PahoPublisher.Instance().publish((config["BROKER_DEVICE_EVENTS_TOPIC"] % device_id), device_id,
                                             event.to_json(allow_nan=False))
            logger.info("Device metadata sent [device-id: %s]" % device_id)
            return True

        except HTTPError as err:
            raise RuntimeError("Device metadata not sent", err.args)

        except Exception as ex:
            raise RuntimeError("Device metadata not sent", ex.args)
        return False

    @classmethod
    def _send_platform_attributes_internal(cls):

        data = dict()
        for e in list(PlatformAttribute.objects.values_list('name', 'value')):
            data[e[0]] = e[1]

        try:
            event = actions_events.PlatformEvent.construct_platform_attributes(data)
            PahoPublisher.Instance().publish((config["BROKER_ATTRIBUTES_TOPIC"]), "all", event.to_json(allow_nan=False))
            logger.info("Platform attributes sent")
            return True

        except HTTPError as err:
            raise RuntimeError("Platform attributes not sent", err.args)

        except Exception as ex:
            raise RuntimeError("Platform attributes not sent", ex.args)
        return False