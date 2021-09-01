import os
import sys

import pytz
from django.apps import AppConfig


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

        from app.tasks import update_connections
        update_connections.apply_async()
        print("Sent initial health / connection collect tasks")

        from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule
        if IntervalSchedule.objects.count() <= 0:
            print("No scheduled data found in DB, initializing ...")

            schedule, created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)
            PeriodicTask.objects.create(interval=schedule,
                                        name='RabbitMQ connections sync',
                                        task='app.tasks.update_connections')

            schedule2, created2 = IntervalSchedule.objects.get_or_create(every=30, period=IntervalSchedule.SECONDS)
            PeriodicTask.objects.create(interval=schedule2,
                                        name='RabbitMQ health check',
                                        task='app.tasks.check_system_health')

            schedule3, created3 = CrontabSchedule.objects.get_or_create(
                minute='5', hour='*', day_of_week='*', day_of_month='*', month_of_year='*',
                timezone=pytz.utc)
            PeriodicTask.objects.create(interval=schedule3,
                                        name='Export raw data to CSV',
                                        task='app.tasks.export_raw_data_to_csv')

            print("Initialized scheduled system tasks ...")
