import json
from datetime import datetime
from random import uniform, triangular


def date_converter(o):
    if isinstance(o, datetime):
        return o.__str__()


def random_sensor_data(device_id, client_id):
    multi = float(uniform(1, 2))
    message = {
        "device_id": device_id,
        "client_id": client_id,
        "time": datetime.utcnow(),
        "data": {
            "temperature": ("%.2f" % uniform(10.0 * multi, 10.0 * multi)),
            "humidity": ("%.1f" % uniform(1.0 * multi, 2.0 * multi)),
            "NO2": ("%.1f" % uniform(1.0 * multi, 2.0 * multi)),
            "SO2": ("%.1f" % uniform(1.0 * multi, 2.0 * multi)),
            "PM10": ("%.1f" % triangular(1.0 * multi, 2.0 * multi)),
            "PM25": ("%.1f" % triangular(1.0 * multi, 2.0 * multi))
        }
    }
    return json.dumps(message,
                      default=date_converter,
                      sort_keys=False,
                      indent=None,
                      separators=(',', ':'))
