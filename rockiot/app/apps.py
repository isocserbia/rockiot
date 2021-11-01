import os
import sys

from django.apps import AppConfig
from health_check.plugins import plugin_dir


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):

        from app.models import AlertScheme, MAX_MINUTES_NO_METADATA, MAX_TERMINATED_CONNECTIONS_PER_HOUR, \
            MAX_MINUTES_NO_INGEST, \
            MAX_MINUTES_OFFLINE, Device
        from app.system.healthchecks import DevicesOnlineHC
        plugin_dir.register(DevicesOnlineHC)

        run_once = os.environ.get('APPS_RUN_ONCE')
        if run_once is not None or 'runserver' not in sys.argv:
            return

        os.environ['APPS_RUN_ONCE'] = 'True'




