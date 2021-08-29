import os
import sys

from django.apps import AppConfig
from app.rabbitops.rabbit_task import RabbitTask


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        run_once = os.environ.get('APPS_RUN_ONCE')
        if run_once is not None or 'runserver' not in sys.argv:
            return

        os.environ['APPS_RUN_ONCE'] = 'True'
        from app.models import Device
        from django.contrib.auth.models import User
        from app.rabbitops.rabbit_pika_task_consumer import ReconnectingRabbitPikaTaskConsumer
        consumer = ReconnectingRabbitPikaTaskConsumer()
        consumer.daemon = True
        consumer.start()
        print("Started rabbit pika consumer thread [name: %s]" % consumer.getName())

        from app.rabbitops.rabbit_task_producer import RabbitTaskProducer
        # RabbitTaskProducer.publish_delayed_task(RabbitTask("check_devices_health", 0))
        # RabbitTaskProducer.publish_delayed_task(RabbitTask("check_connection", 0))
        RabbitTaskProducer.publish_delayed_task(RabbitTask("list_connections", 0))
        print("Sent initial health / connection collect tasks")
