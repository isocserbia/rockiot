import os
import sys

from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        if os.environ.get('TASKS_RUN_ONCE') is not None or 'runserver' not in sys.argv:
            return
        else:
            os.environ['TASKS_RUN_ONCE'] = 'True'
