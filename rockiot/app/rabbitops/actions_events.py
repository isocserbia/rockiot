from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(init=True)
class PlatformEvent:
    type: str
    sent_at: str
    attributes: Optional[dict] = None

    @classmethod
    def construct_platform_attributes(cls, attributes):
        return PlatformEvent("platform_attributes", datetime.utcnow().isoformat(), attributes)


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
    previous_status: str
    new_status: str
    message: str
    sent_at: str
    type: str = "status"
    data: Optional[dict] = None

    @classmethod
    def construct_status(cls, previous_status, new_status, message):
        return DeviceEvent(previous_status, new_status, message,
                           datetime.utcnow().isoformat(), "status", None)

    @classmethod
    def construct_activation(cls, previous_status, new_status, message):
        return DeviceEvent(previous_status, new_status, message,
                           datetime.utcnow().isoformat(), "activation", None)

    @classmethod
    def construct_device_event(cls, event_type):
        return DeviceEvent(None, None, None, datetime.utcnow().isoformat(), "device_config", {f"{event_type}": True})

    @classmethod
    def construct_device_metadata_changed(cls, metadata):
        return DeviceEvent(None, None, None, datetime.utcnow().isoformat(), "device_metadata", metadata)