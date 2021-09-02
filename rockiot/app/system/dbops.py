#!/usr/bin/env python

import logging
from datetime import date

import psycopg2
from django.conf import settings

config = settings.DATABASES["default"]
logger = logging.getLogger(__name__)


def export_raw_data_to_csv(dat=date.today().isoformat()):

    file_path = f"/rockiot-data/sensor_data-{dat}.csv"
    logger.info(f"Preparing for CSV data export {file_path}")

    db_args = dict(host=config["HOST"], port=config["PORT"], dbname=config["NAME"],
                   user=config["USER"], password=config["PASSWORD"])
    db_conn = psycopg2.connect(**db_args)
    db_cursor = db_conn.cursor()

    query = f"SELECT * FROM sensor_data WHERE date_trunc('day', time) = '{dat}'"
    query_csv = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(query)

    try:
        logger.info(f"Extracting sensor data with query: {query_csv}")
        with open(file_path, 'w') as f_output:
            db_cursor.copy_expert(query_csv, f_output)
        logger.info(f"Sensor data exported to: {file_path}")
    except psycopg2.Error as e:
        logger.error("Error running sensor data copy csv query", e)

    db_cursor.close()
    db_conn.close()
    return file_path


if __name__ == '__main__':
    export_raw_data_to_csv()
