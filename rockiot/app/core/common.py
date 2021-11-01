import json


def validate_json(data):
    try:
        json.loads(data)
    except:
        return False
    return True
