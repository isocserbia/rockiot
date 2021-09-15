from dataclasses import dataclass
from datetime import datetime

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(init=True)
class AttributesEvent:
    name: str
    old_value: str
    new_value: str
    sent_at: str


@dataclass_json
@dataclass(init=True)
class DeviceAction:
    type: str
    client_id: str
    correlation_id: str
    sent_at: str


@dataclass_json
@dataclass(init=True)
class DeviceEvent:
    previous_status: str
    new_status: str
    message: str
    sent_at: str
    type: str = "status"

    @classmethod
    def construct_status(cls, previous_status, new_status, message):
        return DeviceEvent(previous_status, new_status, message,
                           datetime.utcnow().isoformat(), "status")

    @classmethod
    def construct_activation(cls, previous_status, new_status, message):
        return DeviceEvent(previous_status, new_status, message,
                           datetime.utcnow().isoformat(), "activation")

