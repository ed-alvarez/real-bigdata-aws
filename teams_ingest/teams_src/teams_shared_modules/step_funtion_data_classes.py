from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from teams_src.teams_shared_modules.teams_data_classes import to_json_shared


@dataclass
class TeamsEvent:
    firm: str
    period: str
    tenant_name: str
    tenant_id: str
    start_date: Optional[datetime] = ""
    end_date: Optional[datetime] = ""
    user_ids: Optional[list] = field(default_factory=list)

    def to_json(self):
        return to_json_shared(self)


@dataclass
class TeamsDecode(TeamsEvent):
    files_to_process: bool = False
    workflow_done: bool = False
    list_of_files_to_process: List = field(default_factory=list)
    list_of_files_processed: List = field(default_factory=list)

    def to_json(self):
        return to_json_shared(self)


###########################
# For Launch Trigger Lambda
@dataclass
class LaunchIngestChannel:
    firm: str
    tenant_name: str
    period: str
    tenant_id: str
    start_date: Optional[str] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    end_date: Optional[str] = datetime.now().strftime("%Y-%m-%d")

    def to_json(self):
        return to_json_shared(self)
