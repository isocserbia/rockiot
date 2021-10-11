from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(init=True)
class PlatformEvent:
    type: str
    sent_at: str
    attributes: Optional[dict] = None


@dataclass_json
@dataclass(init=True)
class DeviceAction:
    type: str
    client_id: str
    correlation_id: str
    sent_at: str
    data: Optional[dict] = None


@dataclass_json
@dataclass(init=True)
class DeviceEvent:
    type: str
    previous_status: Optional[str]
    new_status: Optional[str]
    message: Optional[str]
    sent_at: str
    data: Optional[dict] = None
