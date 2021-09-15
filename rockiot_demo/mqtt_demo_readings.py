import json
from datetime import datetime
from random import uniform, triangular


def date_converter(o):
    if isinstance(o, datetime):
        return o.__str__()


def random_sensor_data(client_id):
    multi = float(uniform(1, 2))
    message = {
        "client_id": client_id,
        "sent_at": datetime.utcnow().isoformat(),
        "data": {
            "temperature": round(uniform(10.0 * multi, 10.0 * multi), 4),
            "humidity": round(uniform(1.0 * multi, 2.0 * multi), 4),
            "NO2": round(uniform(1.0 * multi, 2.0 * multi), 4),
            "SO2": round(uniform(1.0 * multi, 2.0 * multi), 4),
            "PM1": round(triangular(1.0 * multi, 2.0 * multi), 4),
            "PM10": round(triangular(1.0 * multi, 2.0 * multi), 4),
            "PM2_5": round(triangular(1.0 * multi, 2.0 * multi), 4)
        }
    }
    return json.dumps(message,
                      default=date_converter,
                      sort_keys=False,
                      indent=None,
                      separators=(',', ':'))
