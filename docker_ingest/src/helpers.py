import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

import dataclass_wizard


@dataclass
class DockerLambdaEvent:
    bucket: str
    fetch_ids: Optional[bool] = True
    s3_uris: Optional[List] = field(default_factory=list)
    texts: Optional[List] = field(default_factory=list)
    done_workflow: bool = False

    def to_json(self):
        result: Dict = asdict(self)
        result: str = json.dumps(obj=result)
        return json.loads(result)


def validate_event_payload(event: Dict[str, Any]):
    return dataclass_wizard.fromdict(DockerLambdaEvent, event)
