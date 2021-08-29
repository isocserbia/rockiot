import json
from datetime import datetime
from random import uniform, triangular


def date_converter(o):
    if isinstance(o, datetime):
        return o.__str__()


def random_sensor_data(device_id, client_id, school_id):
    message = {
        "device_id": device_id,
        "client_id": client_id,
        "time": datetime.utcnow(),
        "data": {
            "temperature": ("%.2f" % uniform(10.0 * (float(school_id) - 1), 10.0 * (float(school_id) + 1))),
            "humidity": ("%.1f" % uniform(1.0 * (float(school_id) - 1), 1.0 * (float(school_id) + 1))),
            "NO2": ("%.1f" % uniform(1.0 * (float(school_id) - 1), 1.0 * (float(school_id) + 2))),
            "SO2": ("%.1f" % uniform(1.0 * (float(school_id) - 1), 1.0 * (float(school_id) + 3))),
            "PM10": ("%.1f" % triangular(1.0 * (float(school_id) - 1), 1.0 * (float(school_id) + 1))),
            "PM25": ("%.1f" % triangular(1.0 * (float(school_id) - 1), 1.0 * (float(school_id) + 1)))
        }
    }
    return json.dumps(message,
                      default=date_converter,
                      sort_keys=False,
                      indent=None,
                      separators=(',', ':'))
