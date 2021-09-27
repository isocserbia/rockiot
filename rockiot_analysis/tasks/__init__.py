import os

from celery import Celery
from celery.utils.log import get_task_logger

from tasks.steps.data_loader import initialize_device_measurements_dict
from tasks.steps.model_trainer import train_models
from tasks.steps.entry_scorer import check_scores_for_latest_sensor_data

logger = get_task_logger(__name__)

broker_user = os.getenv("RABBITCELERY_USER", "rabbitcelery")
broker_pass = os.getenv("RABBITCELERY_PASS", "rabbitcelery_pass")
broker_host = os.getenv("BROKER_HOST", "rabbit1")
broker_port = int(os.getenv("BROKER_AMQP_PORT", "5672"))
broker_vhost = os.getenv("BROKER_VHOST", "/")

app = Celery('tasks',
             broker=f'amqp://{broker_user}:{broker_pass}@{broker_host}:{broker_port}/{broker_vhost}')


@app.task(rate_limit='50/m')
def train_model():
    logger.info("Started training models")
    devices_dict = initialize_device_measurements_dict()
    trained_count = train_models(devices_dict)
    logger.info(f"Completed {trained_count} models. ")


@app.task(rate_limit='10/m')
def check_latest_scores():
    logger.info("Started checking latest scores")
    check_scores_for_latest_sensor_data()
    logger.info(f"Completed score check.")


app.conf.worker_prefetch_multiplier = 2

app.conf.beat_schedule = {
    'planner': {
        'task': 'tasks.train_model',
        'schedule': 11.0
    },
    'scorer': {
        'task': 'tasks.check_latest_scores',
        'schedule': 22.0
    }
}

if __name__ == '__main__':
    logger.info('Started tasks server')

