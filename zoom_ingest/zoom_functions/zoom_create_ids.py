import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, Union

import aws_lambda_logging
import dataclass_wizard
from aws_lambda_powertools.utilities.typing import LambdaContext

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))  # for any host run-time
sys.path.append(str(tenant_directory))


from zoom_settings import BOTO_LOG_LEVEL, LOG_LEVEL, BucketStage
from zoom_shared.api_client import ZoomAPI
from zoom_shared.zoom_dataclasses import ZoomEvent, ZoomFilesTracker
from zoom_shared.zoom_utils import error_handler, lamda_write_to_s3, update_if_error

logger = logging.getLogger()

# CREATE INITIAL SET OF ELEMENTS TO INGEST (IDs)


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict:
    """Download Zoom Files using Zoom API to the todo S3 bucket

    The input event message is
    {
        "customer": "melqart",
        "ingest_range": "daily", | "custom",
        "start_date": "2022-10-14", OPTIONAL
        "end_date": "2022-10-16" OPTIONAL
    }

    The output event message is
    {
        "customer": "melqart",
        "ingest_range": "daily"
        "bucket_name": "todo",
        "success_step": True,
        "done_workflow": False,
        "if_error": "",
        "calls": [call_log_id, ... ],
        "meets": [meeting_recording_id, ...]
    }
    """
    logger.info(f"KICK OFF EVENT {event}")

    aws_lambda_logging.setup(
        level=LOG_LEVEL,
        boto_level=BOTO_LOG_LEVEL,
        aws_request_id=context.aws_request_id,
        module="%(module)s",
    )

    zoom_event: ZoomEvent = validate_event_payload(event=event)
    result: ZoomFilesTracker = create_initial_call_meet_id_sets(zoom_event)

    return result.to_json()


def validate_event_payload(event: Dict[str, Any]) -> ZoomEvent:
    return dataclass_wizard.fromdict(ZoomEvent, event)


@update_if_error
def create_initial_call_meet_id_sets(zoom_event: ZoomEvent) -> ZoomFilesTracker:
    logger.info(f"Zoom Start Ingest Create: {zoom_event} ")

    zoom_result_bus: ZoomFilesTracker = dataclass_wizard.fromdict(
        ZoomFilesTracker,
        asdict(zoom_event),
    )

    calls: List = []
    meets: List = []
    calls, meets = load_ids_from_api(zoom_event)

    if calls or meets:
        zoom_result_bus: ZoomFilesTracker = ZoomFilesTracker(
            customer=zoom_event.customer,
            ingest_range=zoom_event.ingest_range,
            start_date=zoom_event.start_date,
            end_date=zoom_event.end_date,
            calls=calls,
            meets=meets,
            bucket_name=BucketStage.TODO.value,
            success_step=True,
        )

    logger.info(f"Zoom Start Ingest Zoom Event: {asdict(zoom_result_bus)} ")

    return zoom_result_bus


@error_handler
def load_ids_from_api(zoom_event: ZoomEvent) -> Iterable[Union[bool, str]]:
    initial_sets_to_ingest, is_there_data = create_ids_from_api(event=zoom_event)
    if is_there_data:
        write_push_to_s3(initial_sets_to_ingest, zoom_event.customer)

    call_ids: List[str] = _get_created_set("call_ids", "CALLS", initial_sets_to_ingest)
    meet_ids: List[str] = _get_created_set("meet_ids", "MEETS", initial_sets_to_ingest)
    return call_ids, meet_ids


@error_handler
def _get_created_set(
    set_to_fetch: str, set_type: str, create_sets_result: Dict
) -> List[str]:
    created_set = list(create_sets_result.get(f"{set_to_fetch}", []))
    logger.info(f"Set creation results for {set_type} = {len(created_set)}")
    logger.debug(f"Set creation results for {set_type} = {created_set}")
    return created_set


@error_handler
def create_ids_from_api(event: ZoomEvent) -> Tuple:
    zoom_client = ZoomAPI(event.customer, event.start_date, event.end_date)
    zoom_client.ingest(init_step=True)  # gets all ids on API

    call_ids_set: list = list(set(zoom_client.call_logs_ids))
    meet_ids_set: list = list(set(zoom_client.meet_ids))
    is_data: bool = bool(call_ids_set or meet_ids_set)

    lambda_ = lambda list_tuplet: [[tuplet[0], tuplet[1]] for tuplet in list_tuplet]

    return {"call_ids": call_ids_set, "meet_ids": lambda_(meet_ids_set)}, is_data


@error_handler
def write_push_to_s3(initial_sets_to_ingest: dict, customer: str) -> None:
    lamda_write_to_s3(
        obj=initial_sets_to_ingest,
        prefix_stage="initial_sets",
        customer=customer,
    )
