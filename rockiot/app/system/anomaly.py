#!/usr/bin/env python
import collections
# import datetime
import json
import logging

# import psycopg2
from django.conf import settings
# from luminol.anomaly_detector import AnomalyDetector

config = settings.DATABASES["default"]
logger = logging.getLogger(__name__)


def detect_anomalies():
    # db_args = dict(host=config["HOST"], port=config["PORT"], dbname=config["NAME"],
    #                user=config["USER"], password=config["PASSWORD"])
    # db_conn = psycopg2.connect(**db_args)
    # db_cursor = db_conn.cursor()
    #
    response = collections.defaultdict(lambda: collections.defaultdict(dict))
    # try:
    #     ts = collections.defaultdict(lambda: collections.defaultdict(dict))
    #     max_date = datetime.datetime.now() - datetime.timedelta(minutes=10)
    #     db_cursor.execute("SELECT device_id, time, temperature, humidity, no2, so2, pm1, om2_5, pm10 from sensor_data WHERE time >= %s order by device_id, time", (max_date,))
    #     records = db_cursor.fetchall()
    #     logger.info(f"Loaded {len(records)} to analyze for anomalies ...")
    #     for row in records:
    #         ts[row[0]]["temperature"][row[1]] = row[2]
    #         ts[row[0]]["humidity"][row[1]] = row[3]
    #         ts[row[0]]["no2"][row[1]] = row[4]
    #         ts[row[0]]["so2"][row[1]] = row[5]
    #         ts[row[0]]["pm1"][row[1]] = row[6]
    #         ts[row[0]]["pm2_5"][row[1]] = row[7]
    #         ts[row[0]]["pm10"][row[1]] = row[8]
    #
    #     for k, v in ts.items():
    #         for sensor, readings in v.items():
    #             my_detector = AnomalyDetector(readings, score_threshold=1.5)
    #             anomalies = my_detector.get_anomalies()
    #             for a in anomalies:
    #                 a_dict = a.__dict__
    #                 for key in a_dict:
    #                     logger.warn(f"{k} / {sensor} anomaly: {a_dict[key]}")
    #                     response[k][sensor][key] = a_dict[key]
    #
    #     db_cursor.close()
    #
    # except psycopg2.Error as e:
    #     logger.error("Error running anomaly detect process", e)
    #     db_conn.rollback()
    #
    # db_conn.close()
    return json.dumps(response)
