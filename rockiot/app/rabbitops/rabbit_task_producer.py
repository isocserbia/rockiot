import logging

import pika
from django.conf import settings

from app.rabbitops.rabbit_task import RabbitTask

config = settings.BROKER_CONFIG
logger = logging.getLogger(__name__)


class RabbitTaskProducer:

    @staticmethod
    def publish_task(task: RabbitTask):
        json_body = task.to_json()
        logger.info("Publishing task [body: %s] " % json_body)
        channel = RabbitTaskProducer._get_connection().channel()
        channel.basic_publish(exchange='', routing_key=config['BROKER_TASK_QUEUE'], body=json_body)
        channel.close()

    @staticmethod
    def publish_delayed_task(task: RabbitTask):
        json_body = task.to_json()
        logger.info("Publishing delayed task [body: %s] " % json_body)
        channel = RabbitTaskProducer._get_connection().channel()
        channel.basic_publish(exchange='', routing_key=config['BROKER_DELAYED_TASK_QUEUE'], body=json_body)
        channel.close()

    @classmethod
    def _get_connection(cls):
        credentials = pika.credentials.PlainCredentials(
            username=config['AMQPTASKPRODUCER_USER'],
            password=config['AMQPTASKPRODUCER_PASS']
        )
        parameters = pika.ConnectionParameters(
            host=config['BROKER_HOST'],
            credentials=credentials,
            port=config['BROKER_AMQP_PORT'],
            heartbeat=60
        )
        return pika.BlockingConnection(parameters)
