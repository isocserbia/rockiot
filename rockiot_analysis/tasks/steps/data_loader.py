import collections
import os
import psycopg2
import psycopg2.extras
from celery.utils.log import get_task_logger

from tasks.steps.config import sensors

logger = get_task_logger(__name__)

TS_HOST = os.getenv("TS_HOST", default='timescaledb')
TS_PORT = int(os.getenv("TS_PORT", default='5432'))
TS_DB = os.getenv("TS_DB", default='rock_iot')
TS_USER = os.getenv("TS_USER", default='postgres')
TS_PASS = os.getenv("TS_PASS", default='postgres')

conn_args = dict(host=TS_HOST, port=TS_PORT, database=TS_DB, user=TS_USER, password=TS_PASS)
db_conn = psycopg2.connect(**conn_args)
db_conn_2 = psycopg2.connect(**conn_args)


def insert_demo_readings():
    db_cursor = db_conn.cursor()
    db_cursor.execute(
        """
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 00:00:00', 'device3', 0, 0, 0, 0, 0, 0, 0);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 01:00:00', 'device3', 1, 1, 1, 1, 1, 1, 1);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 02:00:00', 'device3', 1, 1, 1, 1, 1, 1, 1);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 03:00:00', 'device3', 1, 1, 1, 1, 1, 1, 1);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 04:00:00', 'device3', 0, 0, 0, 0, 0, 0, 0);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 05:00:00', 'device3', 1, 1, 1, 1, 1, 1, 1);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 06:00:00', 'device3', 1, 1, 1, 1, 1, 1, 1);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 07:00:00', 'device3', 1, 1, 1, 1, 1, 1, 1);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 08:00:00', 'device3', 0, 0, 0, 0, 0, 0, 0);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 09:00:00', 'device3', 1, 1, 1, 1, 1, 1, 1);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 10:00:00', 'device3', 1, 1, 1, 1, 1, 1, 1);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 11:00:00', 'device3', 1, 1, 1, 1, 1, 1, 1);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 12:00:00', 'device3', 0, 0, 0, 0, 0, 0, 0);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 13:00:00', 'device3', 1, 1, 1, 1, 1, 1, 1);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 14:00:00', 'device3', 1, 1, 1, 1, 1, 1, 1);
        INSERT INTO sensor_data_rollup_1h (time, device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
        VALUES('2020-09-24 15:00:00', 'device3', 1, 1, 1, 1, 1, 1, 1);
        """)
    db_cursor.close()
    db_conn.commit()


def initialize_device_measurements_dict():
    devices_dict = collections.defaultdict(lambda: collections.defaultdict(dict))
    db_cursor = db_conn.cursor()
    db_cursor.execute("select device_id from app_device")
    devices = db_cursor.fetchall()
    for d in devices:
        for s in sensors:
            devices_dict[d[0]][s] = {}

    db_cursor.close()
    db_cursor = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    for k in devices_dict.keys():
        for s in sensors:
            devices_dict[k][s] = []
        db_cursor.execute(
            f"SELECT time, temperature, humidity, no2, so2, pm1, pm2_5, pm10 FROM sensor_data_rollup_1h WHERE device_id = '{k}' ORDER BY time DESC LIMIT 48")
        data = db_cursor.fetchall()
        for d in sorted(data, reverse=True):
            # print(f"Loaded data {d}")
            for s in sensors:
                devices_dict[k][s].append(
                    {'index': d[0].strftime("%H:%M:%S"), 'value': d.get(s), 'interpolated': d.get(s)})

    db_cursor.close()
    return devices_dict
