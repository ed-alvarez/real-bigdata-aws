import datetime
import functools
import json
import logging
import sys
import time
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any, List, Optional, Tuple

import dataclass_wizard
from dateutil.parser import parse

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))

from zoom_settings import INGEST_SOURCE, STAGE, BucketStage, FileExtension, zoomType
from zoom_shared.zoom_dataclasses import CDR, PersonaDetails, Recording, Transcript

from shared.shared_src.s3.s3_helper import S3Helper

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def how_many_call_ids(event_call_ids: list) -> int:
    count = 0
    for item in event_call_ids:
        if "raw" not in item and "ready" not in item:
            count = count + 1
    return count


def how_many_meet_id_lists(event_meet_ids) -> int:
    count = 0
    for item in event_meet_ids:
        if isinstance(item, list):
            count = count + 1
    return count


def pending_call_ids(call_tracker: list) -> Optional[str]:
    for item in call_tracker:
        if "raw" not in item and "ready" not in item:
            return call_tracker.pop(call_tracker.index(item))
    return None


def pending_meet_ids(meet_tracker: list) -> Optional[int]:
    for item in meet_tracker:
        if isinstance(item, list):
            return meet_tracker.pop(meet_tracker.index(item))
    return None


def pending_raw_blob_call(call_tracker: list) -> Optional[str]:
    for item in call_tracker:
        if "raw" in item:
            return item
    return None


def pending_raw_blob_meet(meet_tracker: list) -> Optional[str]:
    for item in meet_tracker:
        if "raw" in item:
            return item
    return None


def get_uri_to_process(calls: List, meets: List) -> str:
    if calls:
        for call_uri in calls:
            if "ready" in call_uri:
                return calls.pop(calls.index(call_uri))
    if meets:
        for meet_uri in meets:
            if "ready" in meet_uri:
                return meets.pop(meets.index(meet_uri))

    return "Finished"


def error_handler(func, raise_error: bool = True):
    @functools.wraps(func)
    def _catch_exception(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
            return value
        except ConnectionError as error:
            logger.exception(f"{func.__name__} time out error: {error}")
            if raise_error:
                raise
        except KeyError as error:
            logger.exception(f"{func.__name__} wrong attr: {error}")
            if raise_error:
                raise
        except Exception as error:
            logger.exception(f"{func.__name__} raised exception: {error}")
            if raise_error:
                raise

    return _catch_exception


def update_if_error(func):
    @functools.wraps(func)
    def _step_workflow(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
            return value
        except Exception as error:
            zoom_event_bus = args[0]
            logger.error(f"{func.__name__} | {error}")
            zoom_event_bus.if_error = str(error)
            zoom_event_bus.success_step = False
            return zoom_event_bus

    return _step_workflow


def is_transcript_audio_recordings(meet_recordings: list) -> Optional[dict]:
    _transcript_cloud_recording: list = [
        recording
        for recording in meet_recordings
        if recording["file_extension"] == "VTT"
    ]

    transcript_cloud_recording: dict = (
        _transcript_cloud_recording[0] if len(_transcript_cloud_recording) == 1 else {}
    )

    _audio_cloud_recording: list = [
        recording
        for recording in meet_recordings
        if recording["file_extension"] == "M4A"
    ]
    audio_cloud_recording: dict = (
        _audio_cloud_recording[0] if len(_audio_cloud_recording) == 1 else {}
    )

    return transcript_cloud_recording, audio_cloud_recording


def lamda_write_to_s3(
    obj: Any,
    prefix_stage: str,
    customer: str,
    ingest_source: str = INGEST_SOURCE,
    bucket_stage: str = BucketStage.TODO.value,
    extension: str = FileExtension.JSON.value,
    date_from_event: str = "",
) -> str:
    file_name: str = _create_file_name(
        prefix_stage=prefix_stage, obj=obj, date_from_event=date_from_event
    )
    full_file_key: str = _create_full_file_key(
        bucket_stage, ingest_source, file_name, extension
    )

    obj_to_bytes: Any = _obj_to_bytes(obj)

    s3_client: S3Helper = S3Helper(client_name=customer, ingest_type=ingest_source)

    logger.info(
        f"S3 Bucket {s3_client._bucket_name} WRITING {full_file_key} | For Obj {type(obj)}"
    )
    if prefix_stage != "audio" or prefix_stage != "transcript":
        logger.debug(
            f"S3 Bucket {s3_client._bucket_name} WRITING {full_file_key} | For Obj {type(obj)} \n {obj}"
        )
    s3_client.write_file_to_s3(file_key=full_file_key, file_content=bytes(obj_to_bytes))
    return full_file_key


def _create_full_file_key(bucket_stage, ingest_source, file_name, extension):
    if "dev" in STAGE:
        return f"dev-{bucket_stage}.{ingest_source}/{file_name}.{extension}"
    else:
        return f"{bucket_stage}.{ingest_source}/{file_name}.{extension}"


def _obj_to_bytes(obj: Any) -> Any:
    if isinstance(obj, bytes):
        return obj
    elif isinstance(obj, dict):
        return json.dumps(obj).encode("UTF-8")
    else:
        return json.dumps(asdict(obj)).encode("UTF-8")


def _create_file_name(prefix_stage: str, obj: Any, date_from_event) -> str:
    ts_ms: time = int(time.time() * 1000)
    formatted_date: datetime = date_from_event or date.today().strftime("%Y-%m-%d")
    file_name: str = _concat_file_prefix_name(prefix_stage, obj)
    return f"{formatted_date}/{file_name}_{ts_ms}"


def _concat_file_prefix_name(prefix_stage: str, obj: Any) -> str:
    if "audio" in prefix_stage or "init" in prefix_stage or "final" in prefix_stage:
        return f"dev-{prefix_stage}" if "dev" in STAGE else prefix_stage

    if "cdr" in prefix_stage or "transcript" in prefix_stage:
        zoom_blob_type: str = obj.source.source_type
        zoom_blob_id: str = str(obj.source.source_id)
    else:
        zoom_blob_type: str = obj.cdr.source.source_type
        zoom_blob_id: str = str(obj.cdr.source.source_id)

    if "dev" in STAGE:
        return f"dev-{prefix_stage}_{zoom_blob_type}_{zoom_blob_id}"
    else:
        return f"{prefix_stage}_{zoom_blob_type}_{zoom_blob_id}"


def flatten_json(json_obj: dict) -> dict:
    out: dict = {}

    def flatten(obj_to_flatten: dict, key_name=""):
        if type(obj_to_flatten) is dict:
            for atrr in obj_to_flatten:
                flatten(obj_to_flatten[atrr], key_name + atrr + "_FP_")
        elif type(obj_to_flatten) is list:
            index = 0
            for atrr in obj_to_flatten:
                flatten(atrr, key_name + str(index) + "_FP_")
                index += 1
        else:
            out[key_name[:-1]] = obj_to_flatten

    flatten(json_obj)
    return out


def _parse_date(date: date, fmt=None) -> str:
    if fmt is None:
        fmt = "%Y-%m-%d %H:%M:%S"  # Defaults to : 2022-08-31 07:47:30
    get_date_obj = parse(str(date))
    return str(get_date_obj.strftime(fmt))


def _unknown_call_details(call_details: dict, direction: str) -> dict:
    reduce_details: dict = {}
    reduce_details["id"] = "Unknown"
    reduce_details["first_name"] = "Unknown"
    reduce_details["last_name"] = "Unknown"
    reduce_details["email"] = "Unknown"
    reduce_details["dept"] = "Unknown"
    reduce_details["caller_did_number"] = (
        call_details["caller_number"] if direction == "outbound" else None
    )
    reduce_details["callee_did_number"] = (
        call_details["caller_number"] if direction == "inbound" else None
    )
    return reduce_details


def _empty_transcript(call_id):
    transcript_details = {}
    transcript_details["source_id"] = call_id
    transcript_details["source_type"] = zoomType.call.value
    transcript_details["type"] = "needs-transcript"
    today = date.today()
    formatted_date: str = today.strftime("%Y-%m-%d %H:%M:%S")
    transcript_details["recording_id"] = "needs-transcript"
    transcript_details["recording_start"] = formatted_date
    transcript_details["recording_end"] = formatted_date
    transcript_details["content"] = {}
    return transcript_details


def generate_cdr_call(persona_details: dict, call_details: dict) -> CDR:
    call_details["source_type"] = zoomType.call.value
    call_details["date_time"] = _parse_date(date=call_details["date_time"])

    if call_details["direction"] == "inbound":
        call_details["callee_did_number"] = call_details.get(
            "callee_did_number",
            call_details.get("callee_number"),
        )

        destination_from: PersonaDetails = PersonaDetails.build_full_details_call(
            {**persona_details, **call_details},
            "inbound",
        )

        reduce_details = _unknown_call_details(call_details, "inbound")
        origin_to: PersonaDetails = PersonaDetails.build_few_details_call(
            reduce_details, "inbound"
        )

    elif call_details["direction"] == "outbound":
        call_details["caller_did_number"] = call_details.get(
            "caller_did_number",
            call_details.get("caller_number"),
        )

        origin_to: PersonaDetails = PersonaDetails.build_full_details_call(
            {**persona_details, **call_details},
            "outbound",
        )

        reduce_details = _unknown_call_details(call_details, "outbound")
        destination_from: PersonaDetails = PersonaDetails.build_few_details_call(
            reduce_details, "outbound"
        )

    cdr: CDR = CDR.build_from_objs(origin_to, destination_from, call_details)
    return cdr


def generate_cdr_meet(
    meet_details: dict, persona_details: dict, participants: list = []
) -> CDR:
    meet_details["source_type"] = zoomType.meet.value
    meet_details["date_time"] = _parse_date(date=meet_details["start_time"])
    origin_to: PersonaDetails = PersonaDetails.build_host_meet(persona_details)
    meet_details["id"] = meet_details["id"]
    cdr: CDR = CDR.build_from_objs(
        origin=origin_to, event_details=meet_details, participants=participants
    )
    return cdr


def generate_transcript_call(zoom_transcript: dict, call_id: str) -> Transcript:
    zoom_transcript["source_id"] = call_id
    zoom_transcript["source_type"] = zoomType.call.value
    zoom_transcript["start_time"] = _parse_date(date=zoom_transcript["recording_start"])
    zoom_transcript["end_time"] = _parse_date(date=zoom_transcript["recording_end"])
    zoom_transcript["content"] = zoom_transcript.get(
        "timeline", zoom_transcript.get("content")
    )

    transcript: Transcript = Transcript.build_from_details(zoom_transcript)
    return transcript


def generate_transcript_meet(zoom_transcript: dict, meet_id: str) -> Transcript:
    if not zoom_transcript:
        zoom_transcript["source_id"] = meet_id.replace("/", "$")
        zoom_transcript["source_type"] = zoomType.meet.value
        zoom_transcript["start_time"] = "N/A"
        zoom_transcript["end_time"] = "N/A"
        zoom_transcript["file_extension"] = "AWS-Transcript-Needed"
        zoom_transcript["recording_id"] = meet_id
        zoom_transcript["content"] = {}
    else:
        zoom_transcript["source_id"] = meet_id.replace("/", "$")
        zoom_transcript["source_type"] = zoomType.meet.value
        zoom_transcript["start_time"] = _parse_date(
            date=zoom_transcript["recording_start"]
        )
        zoom_transcript["end_time"] = _parse_date(date=zoom_transcript["recording_end"])
        zoom_transcript["content"] = zoom_transcript[
            "download_url"
        ]  # to be downloaded later
        zoom_transcript["recording_id"] = zoom_transcript["id"]

    transcript: Transcript = Transcript.build_from_details(zoom_transcript)
    return transcript


def generate_recording_call(phone_recording: dict, call_id: str) -> Recording:
    phone_recording["source_id"] = call_id
    phone_recording["source_type"] = zoomType.call.value
    phone_recording["recording_id"] = phone_recording["id"]
    phone_recording["play_url"] = phone_recording["file_url"]
    phone_recording["download_url"] = phone_recording[
        "download_url"
    ]  # to be downloaded later
    phone_recording["type"] = phone_recording["file_url"].split(".")[-1]

    recording: Recording = Recording.build_from_details(phone_recording)
    return recording


def generate_recording_meet(meet_audio_recording: dict, meet_id: str) -> Recording:
    meet_audio_recording["source_id"] = meet_id
    meet_audio_recording["source_type"] = zoomType.meet.value
    meet_audio_recording["recording_id"] = meet_audio_recording["id"]

    recording: Recording = Recording.build_from_details(meet_audio_recording)
    return recording
