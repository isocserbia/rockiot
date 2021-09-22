#!/usr/bin/env python
import collections
import datetime
import logging

import psycopg2
from psycopg2.extras import execute_values
from django.conf import settings

config = settings.DATABASES["default"]
logger = logging.getLogger(__name__)

allowed_delay = settings.ROCKIOT_CONFIG['PIPELINE_ALLOWED_DELAY_MINUTES']


def clean_and_calibrate_dataframe():
    db_args = dict(host=config["HOST"], port=config["PORT"], dbname=config["NAME"],
                   user=config["USER"], password=config["PASSWORD"])
    db_conn = psycopg2.connect(**db_args)
    db_cursor = db_conn.cursor()

    try:

        calibration_models = collections.defaultdict(lambda: collections.defaultdict(dict))
        db_cursor.execute("""
            select d.device_id, dcm.temperature, dcm.humidity, dcm.no2, dcm.so2, dcm.pm1, dcm.pm2_5, dcm.pm10
            from app_devicecalibrationmodel dcm
            join app_device d on dcm.device_id = d.id
            order by device_id;
        """)
        db_models = db_cursor.fetchall()
        for m in db_models:
            calibration_models[m[0]]['temperature'] = m[1]
            calibration_models[m[0]]['humidity'] = m[2]
            calibration_models[m[0]]['no2'] = m[3]
            calibration_models[m[0]]['so2'] = m[4]
            calibration_models[m[0]]['pm1'] = m[5]
            calibration_models[m[0]]['pm2_5'] = m[6]
            calibration_models[m[0]]['pm10'] = m[7]
        db_cursor.close()

        db_cursor = db_conn.cursor()
        db_cursor.execute("SELECT max(time) FROM sensor_data")
        max_date = db_cursor.fetchone()
        if not max_date or max_date is None or max_date[0] is None:
            max_date = datetime.datetime.now() - datetime.timedelta(days=365)
        else:
            max_date = max_date[0] - datetime.timedelta(minutes=allowed_delay)
        db_cursor.close()

        logger.info(f"CC: found max date: {max_date}")

        db_cursor = db_conn.cursor()
        db_cursor.execute("SELECT * from sensor_data_raw WHERE time >= %s", (max_date,))
        raw_records = db_cursor.fetchall()
        clean_records = []
        for row in raw_records:
            data = row[3]
            if row[1] in calibration_models:
                cmodel = calibration_models[row[1]]
                for key, val in data.items():
                    cmodel_str = cmodel.get(key, "0 1 0").split(sep=" ")
                    a = float(cmodel_str[0])
                    b = float(cmodel_str[1]) * val
                    c = float(cmodel_str[2]) * val * val
                    data[key] = a + b + c
            seq = (row[0], row[1], row[2], data.get('temperature'), data.get('humidity'), data.get('no2'),
                   data.get('so2'), data.get('pm1'), data.get('pm10'), data.get('pm2_5'))
            seq_list = list(seq)
            clean_records.append(seq_list)
        db_cursor.close()

        logger.info(f"CC: Produced {len(clean_records)} clean records")

        db_cursor = db_conn.cursor()
        execute_values(db_cursor,
                       """INSERT INTO sensor_data (time, device_id, client_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5) 
                        VALUES %s ON CONFLICT (device_id, time) DO NOTHING;
                        """,
                       clean_records)

        logger.info(f"CC: Inserted {len(clean_records)} clean records")
        db_cursor.close()
        db_conn.commit()

    except psycopg2.Error as e:
        logger.error("Error running clean and calibrate sensor data", e)
        db_conn.rollback()

    db_conn.close()
