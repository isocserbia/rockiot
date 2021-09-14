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
)

app.conf.database_table_schemas = {
    'task': 'public',
    'group': 'public',
}

app.conf.task_ignore_result = False
app.conf.task_store_errors_even_if_ignored = True

app.conf.task_queues = (
    Queue("normal", Exchange("normal"), routing_key="normal"),
    Queue("low", Exchange("low"), routing_key="low"),
)
app.conf.task_default_queue = "normal"
app.conf.task_default_exchange = "normal"
app.conf.task_default_routing_key = "normal"

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

if __name__ == '__main__':
    app.start()
