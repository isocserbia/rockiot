import os
import pickle

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


def get_model(device_id, sensor):
    model_path = f'/data/analysis_{device_id}_{sensor}.model'
    if not os.path.isfile(model_path):
        return None
    file = open(model_path, 'rb')
    model = pickle.loads(file.read())
    file.close()
    return model


def get_score(device_id, sensor, index, value):
    model = get_model(device_id, sensor)
    if not model:
        return None
    return model.score(value, index)[0]


def check_scores_for_latest_sensor_data():
    db_cursor = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    db_cursor.execute(
        "select device_id, time, temperature, humidity, no2, so2, pm1, pm2_5, pm10 FROM sensor_data ORDER BY time DESC LIMIT 100")
    sensor_data = db_cursor.fetchall()
    results = []
    for row in sensor_data:
        for s in sensors:
            device_id = row.get('device_id')
            time = row.get('time')
            value = row.get(s)
            score = get_score(device_id, s, time, value)
            if score:
                if s == 'temperature':
                    prediction = score.get('Prediction')
                    probability = score.get('AnomalyProbability')
                    logger.debug(f"Result: Device {device_id}, "
                                 f"Sensor: {s}, Time: {time}, Value: {value}, "
                                 f"Anomaly: {score.get('IsAnomaly')}, "
                                 f"Prediction: {prediction}, Probability: {probability}")
                    if score.get('IsAnomaly', False) is True and probability > 0.98:
                        logger.warning(f"Anomaly: {device_id}, {s}, {time}, {value}, "
                                       f"Prediction: {prediction}, Probability: {probability}")
                        results.append({'device_id': device_id, 'sensor': s, 'time': time, 'value': value,
                                        'prediction': prediction, 'probability': probability})
    if results and len(results) > 0:
        logger.warning(f"{len(results)} anomalies detected!")
    else:
        logger.info(f"No anomalies detected.")
    db_cursor.close()
    return results
