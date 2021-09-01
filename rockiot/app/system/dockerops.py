import logging
import sys
import threading

import docker

from app.models import Device

from django.conf import settings

config = settings.BROKER_CONFIG

logger = logging.getLogger(__name__)

ROCKIOT_DEMO_CONTAINER = 'rockiot_demo'
ROCKIOT_DEMO_IMAGE = 'rockiot_project_rockiot_demo'


class DockerOps:
    __lock = threading.Lock()
    __client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    __device_container_map = {}

    @classmethod
    def start_demo_container(cls, device: Device):

        if not device:
            logger.error("Device entity is mandatory")
            return False

        with cls.__lock:
            env = dict(config)
            env['DEVICE_ID'] = device.device_id
            env['DEVICE_PASS'] = device.device_pass

            name = f'{ROCKIOT_DEMO_CONTAINER}_{env["DEVICE_ID"]}'
            containers = cls.__client.containers.list(ignore_removed=False, filters={"name": name})
            if containers and len(containers) > 0:
                container = containers[0]
                if container.status == 'running' or container.status == 'restarting':
                    logger.info(f"Device {device.device_id} container is already {container.status}")
                else:
                    container.start()
                    logger.info(f"Device {device.device_id} container started [name: {container.name}]")
            else:
                container = cls.__client.containers.run(image=ROCKIOT_DEMO_IMAGE, name=name, command="/start.sh",
                                                        detach=True, environment=env, network="rockiot_project_app-tier")
                logger.info(f"Device {device.device_id} container started [name: {container.name}]")

            return True

    @classmethod
    def stop_demo_container(cls, device: Device, restart=False):

        if not device:
            logger.error("Device entity is mandatory")
            return False

        with cls.__lock:
            try:
                name = f'{ROCKIOT_DEMO_CONTAINER}_{device.device_id}'
                containers = cls.__client.containers.list(ignore_removed=True, filters={"name": name})
                if containers and len(containers) > 0:
                    container = containers[0]
                    if restart:
                        container.restart()
                        logger.info(f"Device {device.device_id} container restarted [name: {container.name}]")
                    else:
                        container.stop()
                        container.remove()
                        logger.info(f"Device {device.device_id} container stopped [name: {container.name}]")
                else:
                    logger.info(f"Device {device.device_id} container not found [name: {name}]")
                return True
            except:
                logger.error("Error stopping container", sys.exc_info()[0])
                return False
