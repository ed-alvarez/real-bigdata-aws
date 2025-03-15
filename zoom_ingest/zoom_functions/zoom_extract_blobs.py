import logging
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Tuple

import aws_lambda_logging
import dataclass_wizard
from aws_lambda_powertools.utilities.typing import LambdaContext

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))


from zoom_settings import (
    BOTO_LOG_LEVEL,
    INGEST_SOURCE,
    LOG_LEVEL,
    BucketStage,
    FileExtension,
)
from zoom_shared.api_client import ZoomAPI
from zoom_shared.zoom_dataclasses import ZoomDTO, ZoomFilesTracker
from zoom_shared.zoom_utils import (
    error_handler,
    how_many_call_ids,
    how_many_meet_id_lists,
    lamda_write_to_s3,
    pending_call_ids,
    pending_meet_ids,
    update_if_error,
)

logger = logging.getLogger()


# GENERATE ONE BLOB FROM LIST OF IDs & STORE AT TO-DO BUCKET


@error_handler
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict:
    """
    Input
    {
        "customer": "melqart",
        "ingest_range": "custom",
        "if_error": "",
        "start_date": "2022-09-09",
        "end_date": "2022-09-10",
        "bucket_name": "todo",
        "success_step": True,
        "done_workflow": False,
        "calls": [
            "a6df2784-9ec4-43ce-8845-13275c55da40",
            "25d84204-364f-4975-b38c-ef2fbe7a8c1d",
        ],
        "meets": [6429324446, 8728440253],
    }

    Output
    {
        "customer": "melqart",
        "date_range": "daily",
        "bucket_name": "todo.zoom",
        "success_step": True,
        "done_workflow": False,
        "calls": [raw_call_blob_S3_URI_at_TODO, ... ],
        "meets": [raw_meet_blob_S3_URI_at_TODO, ...]
    }
    """
    aws_lambda_logging.setup(
        level=LOG_LEVEL,
        boto_level=BOTO_LOG_LEVEL,
        aws_request_id=context.aws_request_id,
        module="%(module)s",
    )

    zoom_event_bus: ZoomFilesTracker = validate_event_payload(event=event)
    result: ZoomFilesTracker = extract_blobs(zoom_event_bus)

    return result.to_json()


def validate_event_payload(event: Dict[str, Any]) -> ZoomFilesTracker:
    event = dataclass_wizard.fromdict(ZoomFilesTracker, event)
    event.if_error = {}
    return event


def status_extract(zoom_event_bus: ZoomFilesTracker) -> ZoomFilesTracker:
    ids_call_left: int = how_many_call_ids(zoom_event_bus.calls)
    ids_meets_left: int = how_many_meet_id_lists(zoom_event_bus.meets)
    logger.info(
        f"Blobs to extract from API {ids_call_left} Calls & Meets {ids_meets_left}"
    )
    if ids_call_left == 0 and ids_meets_left == 0:
        zoom_event_bus.success_step = True
        return zoom_event_bus
    return zoom_event_bus


@update_if_error
def extract_blobs(zoom_event_bus: ZoomFilesTracker) -> ZoomFilesTracker:
    logger.info(f"Zoom Extract Blobs Step with event: {asdict(zoom_event_bus)} ")
    zoom_event_bus.success_step = False
    status_extract(zoom_event_bus)

    if not zoom_event_bus.success_step:
        call_blob_uri, meet_blob_uri = do_blobs_for_ids(event_tracker=zoom_event_bus)

        if call_blob_uri:
            zoom_event_bus.calls.append(call_blob_uri)
        if meet_blob_uri:
            zoom_event_bus.meets.append(meet_blob_uri)

        status_extract(zoom_event_bus)
    return zoom_event_bus


@error_handler
def do_blobs_for_ids(event_tracker: ZoomFilesTracker) -> Tuple[str, str]:
    todo_raw_uri_call: str = ""
    todo_raw_uri_meet: str = ""

    api_client: ZoomAPI = ZoomAPI(
        event_tracker.customer, event_tracker.start_date, event_tracker.end_date
    )
    api_client.ingest(init_step=False)

    if event_tracker.calls:
        todo_raw_uri_call = extract_blob_for_call(event_tracker, api_client)

    if event_tracker.meets:
        todo_raw_uri_meet = extract_blob_for_meet(event_tracker, api_client)

    return todo_raw_uri_call, todo_raw_uri_meet


@error_handler
def extract_blob_for_call(event_tracker: ZoomFilesTracker, api_client: ZoomAPI) -> str:
    if call_id := pending_call_ids(event_tracker.calls):
        logger.info(f"Extracting metadata for blob call id = {call_id} ")
        call_blob: ZoomDTO = api_client.generate_cdr_transcript_recording_data_call(
            call_id
        )
        return _write_blob_to_s3(call_blob, event_tracker.customer)


@error_handler
def extract_blob_for_meet(event_tracker: ZoomFilesTracker, api_client: ZoomAPI) -> str:
    if meet_ids := pending_meet_ids(event_tracker.meets):
        logger.info(f"Extracting metadata for blob meet id = {meet_ids[1]} ")
        meet_blob: ZoomDTO = api_client.generate_cdr_transcript_recording_data_meet(
            meet_ids
        )
        return _write_blob_to_s3(meet_blob, event_tracker.customer)


def _write_blob_to_s3(blob_generation_result: ZoomDTO, customer: str) -> str:
    blob_id: str = str(blob_generation_result.recording.source.source_id)
    logger.info(f"Generation of blob id = {blob_id} ")
    logger.debug(f"Generated blob \n {asdict(blob_generation_result)} \n ")

    file_path_uri: str = lamda_write_to_s3(
        obj=blob_generation_result,
        prefix_stage="raw",
        ingest_source=INGEST_SOURCE,
        bucket_stage=BucketStage.TODO.value,
        customer=customer,
        extension=FileExtension.JSON.value,
    )

    logger.debug(f"Stored blob at {file_path_uri} \n ")
    return file_path_uri
