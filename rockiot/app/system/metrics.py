import logging
import threading

import time
from datetime import datetime

import psycopg2
import pytz
from django.conf import settings
from prometheus_client import Gauge

from app.models import AlertScheme

config = settings.DATABASES["default"]
logger = logging.getLogger(__name__)

utc = pytz.UTC


def localized_datetime(dt):
    if not dt:
        return None
    return dt if dt.tzinfo is not None else utc.localize(dt)


def localized_timestamp(dt):
    if not dt:
        return None
    return dt.timestamp() if dt.tzinfo is not None else utc.localize(dt).timestamp()


class MetricsExporter(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.gauge1 = Gauge('metadata_updated_at', "Metadata updated at",
                            labelnames=("device",), namespace="rockiot", subsystem="device")
        self.gauge2 = Gauge('terminated_connections_in_hour', "Number of terminated connections in last hour",
                            labelnames=("device",), namespace="rockiot", subsystem="device")
        self.gauge3 = Gauge('data_updated_at', "Last data ingested at",
                            labelnames=("device",), namespace="rockiot", subsystem="device")
        self.gauge4 = Gauge('last_seen_at', "Last time device was seen online",
                            labelnames=("device",), namespace="rockiot", subsystem="device")

        db_args = dict(host=config["HOST"], port=config["PORT"], dbname=config["NAME"],
                       user=config["USER"], password=config["PASSWORD"])
        self.db_conn = psycopg2.connect(**db_args)

    def run(self):
        while True:
            try:
                time.sleep(15)
                self.export_device_metrics()
            except:
                logger.error("error exporting metrics", exc_info=True)

    def export_device_metrics(self):
        logger.info("Exporting devices metrics ....")
        try:
            for a in AlertScheme.objects.all():
                db_cursor = self.db_conn.cursor()
                db_cursor.execute("""
                select
                     ad.device_id,
                     to_timestamp(ad.metadata->>'sent_at', 'YYYY-MM-DD"T"HH24:MI:SSZ') as metadata_sent_at,
                     (select count(*) from app_deviceconnection where terminated_at >= (now()-interval '1 hour') and device_id = ad.id) "terminated_connections_in_last_hour",
                     (select max(time) from sensor_data_raw where device_id = ad.device_id) "last_entry_at",
                     (select connected_at from app_deviceconnection where terminated_at is NULL and state = 'RUNNING' and device_id = ad.id) "connected_at",
                     (select max(terminated_at) from app_deviceconnection where device_id = ad.id) "terminated_at"
                from app_device ad where ad.alert_scheme_id = %s;
                """, (a.id,))
                devices = db_cursor.fetchall()
                for d in devices:
                    if d[1]:
                        self.gauge1.labels(d[0]).set(localized_timestamp(d[1]))
                    if d[2]:
                        self.gauge2.labels(d[0]).set(d[2])
                    if d[3]:
                        self.gauge3.labels(d[0]).set(localized_timestamp(d[3]))
                    if d[4]:
                        seen_online = d[3] if (d[3] and localized_datetime(d[3]) > localized_datetime(d[4])) else d[4]
                    else:
                        seen_online = d[5]
                    if seen_online:
                        self.gauge4.labels(d[0]).set(localized_timestamp(seen_online))
                db_cursor.close()
        except:
            logger.error("error collecting devices metrics", exc_info=True)
