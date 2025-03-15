import dataclasses
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))

from zoom_settings import BucketStage, zoomType


###########################
# Abstract Factories
def dataclass_factory(schema: Dict, name: str = "DataClassFactory"):
    dataclass_schema: list = [
        (property_name, type(property_value).__name__)
        for property_name, property_value in schema.items()
    ]
    return dataclasses.make_dataclass(cls_name=name, fields=dataclass_schema)


def from_dict_to_dataclass(dict_json: dict, class_name: str):
    factory = dataclass_factory(dict_json, class_name)
    return factory(**dict_json)


###########################
# For Launch Trigger Lambda
@dataclass
class LaunchIngestChannel:
    tenant: str = "zoom"  # change the tenant name
    customer: str = ""
    ingest_range: Optional[str] = ""
    ssm_client_id: Optional[str] = ""  # just add the tenant needed
    ssm_account_id: Optional[str] = ""  # ssm secrets as attr here
    ssm_client_secret: Optional[str] = ""  # will work for all
    start_date: Optional[str] = (datetime.now() - timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )
    end_date: Optional[str] = datetime.now().strftime("%Y-%m-%d")

    def to_json(self):
        result: Dict = asdict(self)
        result: str = json.dumps(obj=result)
        return json.loads(result)


###########################
# For Event Driven Step Functions
@dataclass
class ZoomEvent:
    customer: str = BucketStage.TODO.value
    ingest_range: str = "daily"
    if_error: Optional[Any] = ""
    start_date: Optional[str] = (datetime.now() - timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )
    end_date: Optional[str] = datetime.now().strftime("%Y-%m-%d")

    def to_json(self):
        result: Dict = asdict(self)
        result: str = json.dumps(obj=result)
        return json.loads(result)


@dataclass
class ZoomFilesTracker(ZoomEvent):
    bucket_name: str = ""
    success_step: bool = False
    done_workflow: bool = False
    calls: List = field(default_factory=list)
    meets: List = field(default_factory=list)

    def to_json(self):
        result: Dict = asdict(self)
        result: str = json.dumps(obj=result)
        return json.loads(result)


###########################
# Objs Schemas
@dataclass
class ZoomEntity:
    source_id: str
    source_type: str


@dataclass
class PersonaDetails:
    persona_id: str
    persona_first_name: str
    persona_second_name: str
    persona_number: str
    persona_email: str
    persona_department: str

    @staticmethod
    def build_full_details_call(full_details: dict, direction: str):
        user_details = from_dict_to_dataclass(
            dict_json=full_details, class_name="CallFullDetails"
        )
        return PersonaDetails(
            persona_id=user_details.id,
            persona_first_name=user_details.first_name,
            persona_second_name=user_details.last_name,
            persona_number=user_details.callee_did_number
            if direction == "inbound"
            else user_details.caller_did_number,
            persona_email=user_details.email,
            persona_department=user_details.dept,
        )

    @staticmethod
    def build_few_details_call(dict_details: dict, direction: str):
        some_user_details = from_dict_to_dataclass(
            dict_json=dict_details, class_name="CallFewDetails"
        )
        return PersonaDetails(
            persona_id=some_user_details.id,
            persona_first_name=some_user_details.first_name,
            persona_second_name=some_user_details.last_name,
            persona_number=some_user_details.caller_did_number
            if direction == "outbound"
            else some_user_details.callee_did_number,
            persona_email=some_user_details.email,
            persona_department=some_user_details.dept,
        )

    @staticmethod
    def build_host_meet(host_info: dict):
        user_details = from_dict_to_dataclass(
            dict_json=host_info, class_name="MeetHostDetails"
        )
        return PersonaDetails(
            persona_id=user_details.id,
            persona_first_name=user_details.first_name,
            persona_second_name=user_details.last_name,
            persona_number=user_details.phone_number,
            persona_email=user_details.email,
            persona_department=user_details.dept,
        )

    @staticmethod
    def build_participants_meet(dict_details: dict, direction: str):
        some_user_details = from_dict_to_dataclass(
            dict_json=dict_details, class_name="MeetFewDetails"
        )
        return PersonaDetails(
            persona_id=some_user_details.id,
            persona_first_name=some_user_details.first_name,
            persona_second_name=some_user_details.last_name,
            persona_number=some_user_details.caller_did_number
            if direction == "outbound"
            else some_user_details.callee_did_number,
            persona_email=some_user_details.email,
            persona_department=some_user_details.dept,
        )

    def to_json(self):
        result: Dict = asdict(self)
        result: str = json.dumps(obj=result)
        return json.loads(result)


@dataclass
class CDR:
    source: ZoomEntity
    date_of_action: str
    origin_from: PersonaDetails
    destination_to: Optional[PersonaDetails]  # to combine unto one attr (?)
    participants: Optional[List[Dict]] = field(default_factory=list)

    @staticmethod
    def build_from_objs(
        origin: PersonaDetails,
        destination: PersonaDetails = {},
        event_details: dict = {},
        participants: list = [],
    ):
        cdr_details = from_dict_to_dataclass(
            dict_json=event_details, class_name="EventDetails"
        )
        source: ZoomEntity = ZoomEntity(
            source_id=cdr_details.id, source_type=cdr_details.source_type
        )
        return CDR(
            source=source,
            date_of_action=cdr_details.date_time,
            origin_from=origin,
            destination_to=destination,
            participants=participants,
        )

    def to_json(self):
        result: Dict = asdict(self)
        result: str = json.dumps(obj=result)
        return json.loads(result)


@dataclass
class Transcript:
    type: str
    source: ZoomEntity
    recording_id: str
    start_time: str
    end_time: str
    content: Any

    @staticmethod
    def build_from_details(transcript_details: dict):
        transcript_details = from_dict_to_dataclass(
            dict_json=transcript_details,
            class_name="TranscriptDetails",
        )
        source: ZoomEntity = ZoomEntity(
            source_id=transcript_details.source_id,
            source_type=transcript_details.source_type,
        )
        return Transcript(
            source=source,
            type=transcript_details.type
            if source.source_type == zoomType.call.value
            else transcript_details.file_extension,
            recording_id=transcript_details.recording_id,
            start_time=transcript_details.start_time,
            end_time=transcript_details.end_time,
            content=transcript_details.content,
        )

    def to_json(self):
        result: Dict = asdict(self)
        result: str = json.dumps(obj=result)
        return json.loads(result)


@dataclass
class Recording:
    source: ZoomEntity
    type: str
    play_url: str
    recording_id: str
    download_url: str

    @staticmethod
    def build_from_details(recording_details: dict):
        recording_details = from_dict_to_dataclass(
            dict_json=recording_details, class_name="RecordingDetails"
        )
        source: ZoomEntity = ZoomEntity(
            source_id=recording_details.source_id,
            source_type=recording_details.source_type,
        )
        return Recording(
            source=source,
            type=recording_details.type
            if source.source_type == zoomType.call.value
            else recording_details.file_extension,
            play_url=recording_details.play_url,
            recording_id=recording_details.id,
            download_url=recording_details.download_url,
        )

    def to_json(self):
        result: Dict = asdict(self)
        result: str = json.dumps(obj=result)
        return json.loads(result)


@dataclass
class ZoomDTO:
    cdr: CDR
    transcript: Transcript
    recording: Recording

    def to_json(self):
        result: Dict = asdict(self)
        result: str = json.dumps(obj=result)
        return json.loads(result)
