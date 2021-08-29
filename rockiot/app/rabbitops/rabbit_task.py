from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(init=True)
class RabbitTask:
    type: str
    correlation_id: str
