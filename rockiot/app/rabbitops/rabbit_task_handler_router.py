import logging

from django.conf import settings

from app.rabbitops.rabbit_ops import RabbitOps
from app.rabbitops.rabbit_task import RabbitTask

config = settings.BROKER_CONFIG
logger = logging.getLogger(__name__)


class RabbitTaskHandlerRouter:

    _task_handler_map = {
        "register_device": (RabbitOps, "register_device"),
        "activate_device": (RabbitOps, "activate_device"),
        "activation_request": (RabbitOps, "handle_activation_request"),
        "deactivate_device": (RabbitOps, "deactivate_device"),
        "terminate_device": (RabbitOps, "terminate_device"),
        "check_connection": (RabbitOps, "check_connection"),
        "list_connections": (RabbitOps, "list_connections"),
        "get_overview": (RabbitOps, "get_overview"),
        "check_devices_health": (RabbitOps, "check_devices_health"),
    }

    @staticmethod
    def handle_task(task: RabbitTask):
        logger.info("Handling rabbit task [task: %s]" % task)
        handler = RabbitTaskHandlerRouter._task_handler_map.get(task.type)
        if handler:
            getattr(handler[0], handler[1])(task)
        else:
            logger.error("No handler for given task [type: %s]" % task.type)

