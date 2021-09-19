#!/usr/bin/env python
import datetime
import logging

import psycopg2
from psycopg2.extras import execute_values, Json
from django.conf import settings

config = settings.DATABASES["default"]
logger = logging.getLogger(__name__)


def clean_and_calibrate_dataframe():
    db_args = dict(host=config["HOST"], port=config["PORT"], dbname=config["NAME"],
                   user=config["USER"], password=config["PASSWORD"])
    db_conn = psycopg2.connect(**db_args)
    db_cursor = db_conn.cursor()

    try:
        db_cursor.execute("SELECT max(time) FROM sensor_data_clean")
        max_date = db_cursor.fetchone()
        if not max_date or max_date is None or max_date[0] is None:
            max_date = datetime.datetime.now() - datetime.timedelta(days=365)
        db_cursor.close()

        logger.info(f"CC: found max date: {max_date}")

        db_cursor = db_conn.cursor()
        db_cursor.execute("SELECT * from sensor_data_raw WHERE time >= %s", (max_date,))
        raw_records = db_cursor.fetchall()
        clean_records = []
        for row in raw_records:
            seq = (row[0], row[1], row[2], Json(row[3]))
            seq_list = list(seq)
            clean_records.append(seq_list)
        db_cursor.close()

        logger.info(f"CC: Produced {len(clean_records)} clean records")

        db_cursor = db_conn.cursor()
        execute_values(db_cursor,
                       """INSERT INTO sensor_data_clean (time, device_id, client_id, data) 
                        VALUES %s ON CONFLICT (device_id, time) DO NOTHING;""",
                       clean_records)

        logger.info(f"CC: Inserted {len(clean_records)} clean records")
        db_cursor.close()
        db_conn.commit()

    except psycopg2.Error as e:
        logger.error("Error running clean and calibrate sensor data", e)
        db_conn.rollback()

    db_conn.close()
