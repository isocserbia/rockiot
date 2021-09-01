from dataclasses import dataclass
from dataclasses_json import dataclass_json


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
    type: str
