from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from celery import Celery
import os
from kombu import Queue, Exchange
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

config = settings.BROKER_CONFIG


app = Celery('tasks',
             broker=f'amqp://{config["RABBITCELERY_USER"]}:{config["RABBITCELERY_PASS"]}@{config["BROKER_HOST"]}:{config["BROKER_AMQP_PORT"]}/{config["BROKER_VHOST"]}',
             backend="django-db")

app.config_from_object('django.conf:settings', namespace='CELERY')

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=timedelta(days=7),
    worker_prefetch_multiplier=10,
    task_soft_time_limit=60,
    worker_send_task_events=True,
    task_send_sent_event=True
)

app.conf.database_table_schemas = {
    'task': 'public',
    'group': 'public',
}

app.conf.task_ignore_result = False
app.conf.task_store_errors_even_if_ignored = True

app.conf.task_queues = (
    Queue('celery_default', Exchange("celery_default")),
    Queue("celery_uplink", Exchange("celery_uplink", delivery_mode=1), durable=False),
    Queue("celery_downlink", Exchange("celery_downlink")),
)

app.conf.task_default_queue = "celery_default"
app.conf.task_default_exchange = "celery_default"
app.conf.task_default_routing_key = 'celery_routing_key'

app.conf.task_routes = {
    'app.tasks.register_device': 'celery_downlink',
    'app.tasks.activate_device': 'celery_downlink',
    'app.tasks.deactivate_device': 'celery_downlink',
    'app.tasks.terminate_device': 'celery_downlink',
    'app.tasks.send_device_metadata': 'celery_downlink',
    'app.tasks.send_platform_attributes': 'celery_downlink',
    'app.tasks.send_device_event': {
        'queue': 'celery_downlink',
        'delivery_mode': 'transient',
    },
    'app.tasks.save_device_metadata': 'celery_uplink',
    'app.tasks.handle_activation_request': 'celery_uplink',
    'app.tasks.export_raw_data_to_csv': 'celery_default'
}

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

if __name__ == '__main__':
    app.start()
