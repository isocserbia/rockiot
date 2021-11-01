import logging

from django.conf import settings
from health_check.backends import BaseHealthCheckBackend

from app.system import metrics

config = settings.DATABASES["default"]
logger = logging.getLogger(__name__)


class DevicesOnlineHC(BaseHealthCheckBackend):
    critical_service = False

    def check_status(self):
        logger.info("Exporting devices metrics ....")
        metrics.export_device_metrics()
        return

        # asc = AlertScheme()
        # asc.name = "test"
        # asc.save()
        #
        # try:
        #     db_args = dict(host=config["HOST"], port=config["PORT"], dbname=config["NAME"],
        #                    user=config["USER"], password=config["PASSWORD"])
        #     db_conn = psycopg2.connect(**db_args)
        #     for a in AlertScheme.objects.all():
        #         db_cursor = db_conn.cursor()
        #         db_cursor.execute("""
        #         select
        #              ad.device_id,
        #              to_timestamp(ad.metadata->>'sent_at', 'YYYY-MM-DD"T"HH24:MI:SSZ') as metadata_sent_at,
        #              (select count(*) from app_deviceconnection where terminated_at >= (now()-interval '12 hour') and device_id = ad.id) "terminated_connections_in_last_hour",
        #              (select max(time) from sensor_data_raw where device_id = ad.device_id) "last_entry_at",
        #              (select max(terminated_at) from app_deviceconnection where terminated_at >= (now()-interval '12 hour') and device_id = ad.id and (select count(*) from app_deviceconnection ac where ac.state = 'RUNNING' and ac.device_id = ad.id) <= 0) "terminated_at"
        #         from app_device ad where (ad.alert_scheme_id = %s or ad.alert_scheme_id is null);
        #         """, (a.id, ))
        #         devices = db_cursor.fetchall()
        #         for d in devices:
        #             logger.info(f"Device findings {d[0]} / {d[1]} / {d[2]} / {d[3]} / {d[4]}")
        #             if d[1] is None or d[1] + timedelta(minutes=a.scheme[MAX_MINUTES_NO_METADATA]) < datetime.datetime.now():
        #                 self.add_error(f"Device {d[0]} metadata is too old")
        #             if d[2] and d[2] > a.scheme[MAX_TERMINATED_CONNECTIONS_PER_HOUR]:
        #                 self.add_error(f"Device {d[0]} terminated too many connections")
        #             if d[3] and d[3] + timedelta(minutes=a.scheme[MAX_MINUTES_NO_INGEST]) < datetime.datetime.now():
        #                 self.add_error(f"Device {d[0]} is not ingesting data")
        #             if d[4] and d[4] + timedelta(minutes=a.scheme[MAX_MINUTES_OFFLINE]) < datetime.datetime.now():
        #                 self.add_error(f"Device {d[0]} is offline for too long")
        #         db_cursor.close()
        # except:
        #     logger.error("error performing devices hc", exc_info=True)

    def identifier(self):
        return "DevicesOnlineHC"
