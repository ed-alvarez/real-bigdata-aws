import json
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
sys.path.insert(0, str(root_dir))  # for any host run-time
sys.path.append(str(tenant_directory))

from zoom_settings import (
    BOTO_LOG_LEVEL,
    INGEST_SOURCE,
    LOG_LEVEL,
    PUSH_ES,
    STAGE,
    BucketStage,
    zoomType,
)
from zoom_shared.zoom_dataclasses import (
    CDR,
    Recording,
    Transcript,
    ZoomDTO,
    ZoomFilesTracker,
)
from zoom_shared.zoom_es_parser import push_to_elastic_search
from zoom_shared.zoom_utils import error_handler, get_uri_to_process, lamda_write_to_s3

from shared.shared_src.s3.s3_helper import S3Helper

logger = logging.getLogger()


@error_handler
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict:
    """
    Input
    {
        "customer": "melqart",
        "date_range": "daily",
        "bucket_name": "todo.zoom",
        "success_step": True,
        "done_workflow": False,
        "calls": [call_blob_URI, ... ],
        "meets": [meet_blob_URI, ...]
    }

    Output
    {
        "customer": "melqart",
        "date_range": "daily",
        "bucket_name": "process.dev",
        "success_step": True,
        "done_workflow": True,
        "calls": [call_blob_URI_PROCCESED, ... ],
        "meets": [meet_blob_URI_PROCCESED, ...]
    }
    """

    aws_lambda_logging.setup(
        level=LOG_LEVEL,
        boto_level=BOTO_LOG_LEVEL,
        aws_request_id=context.aws_request_id,
        module="%(module)s",
    )

    zoom_event_bus: ZoomFilesTracker = validate_event_payload(event=event)
    result: ZoomFilesTracker = workflow_process(zoom_event_bus, context.aws_request_id)

    return result.to_json()


def validate_event_payload(event: Dict[str, Any]) -> ZoomFilesTracker:
    event = dataclass_wizard.fromdict(ZoomFilesTracker, event)
    event.if_error = {}
    return event


def workflow_process(
    zoom_result_bus: ZoomFilesTracker, aws_request_id: str
) -> ZoomFilesTracker:
    logger.debug(f"Processing {zoom_result_bus.calls} Calls")
    logger.debug(f"Processing {zoom_result_bus.meets} Meets")

    logger.info(f"Zoom Process Last Step with event: {asdict(zoom_result_bus)} ")

    uri_ready_to_be_processed: str = get_uri_to_process(
        calls=zoom_result_bus.calls,
        meets=zoom_result_bus.meets,
    )
    zoom_result_bus.success_step = False

    if uri_ready_to_be_processed != "Finished":
        logger.info(f"Zoom Processing Ready TODO URI: {uri_ready_to_be_processed} ")

        s3_client: S3Helper = S3Helper(
            client_name=zoom_result_bus.customer,
            ingest_type=INGEST_SOURCE,
        )
        check_and_push_to_es(
            s3_client, zoom_result_bus, uri_ready_to_be_processed, aws_request_id
        )

    if uri_ready_to_be_processed == "Finished":
        zoom_result_bus.success_step = True
        zoom_result_bus.done_workflow = True
        zoom_result_bus.bucket_name = BucketStage.PROCESS.value
        logger.info("Zoom Ingest Finished!")

    return zoom_result_bus


@error_handler
def check_and_push_to_es(
    s3_client: S3Helper,
    zoom_event_bus: ZoomFilesTracker,
    uri_from_todo: str,
    aws_request_id: str,
) -> None:
    customer: str = zoom_event_bus.customer

    todo_ready_blob: ZoomDTO = _get_todo_blob_ready_to_process(
        todo_ready_uri=uri_from_todo,
        s3_client=s3_client,
    )

    logger.info(f"Loaded {todo_ready_blob.cdr.source.source_id} --- ")
    zoom_type: str = todo_ready_blob.cdr.source.source_type

    # 0: URI , 1: Zoom ID
    final_zoom_blob, final_tuplet_reference = write_each_block_individually(
        zoom_final=todo_ready_blob,
        customer=customer,
    )

    processed_uri_path = final_tuplet_reference[1]  # S3 stored final processed blob
    logger.info(f"Final URI at {processed_uri_path} --- ")

    _append_process_uri(zoom_type, processed_uri_path, zoom_event_bus)

    zoom_id = final_tuplet_reference[0]  # the zoom event ID accross all Step ingest

    if archive(final_zoom_blob, zoom_id, customer):
        if PUSH_ES:
            push_to_elastic_search(customer, final_zoom_blob, zoom_id, aws_request_id)
        if "prod" in STAGE:
            s3_client.s3_client.delete_object(
                Bucket=s3_client._bucket_name, Key=uri_from_todo
            )
    else:
        logger.warn("SOMETHING WENT WRONG Should NOT print this --- ")
        exit()


def archive(final_blob, zoom_id, customer) -> bool:
    if final_blob:
        type_ = final_blob.cdr.source.source_type
        lamda_write_to_s3(
            obj=final_blob,
            customer=customer,
            prefix_stage=f"zoom_final_{zoom_id}_{type_}",
            bucket_stage=BucketStage.ARCHIVED.value,
            date_from_event=final_blob.cdr.date_of_action.split(" ")[0],
        )
        return True


def _append_process_uri(
    zoom_type: str, processed_uri_path: str, zoom_event_bus: ZoomFilesTracker
) -> None:
    if zoom_type == zoomType.call.value:
        zoom_event_bus.calls.append(processed_uri_path)
    if zoom_type == zoomType.meet.value:
        zoom_event_bus.meets.append(processed_uri_path)


@error_handler
def write_each_block_individually(
    zoom_final: ZoomDTO,
    customer: str,
) -> Tuple:
    cdr: CDR = zoom_final.cdr
    date_from_event: str = zoom_final.cdr.date_of_action.split(" ")[0]

    cdr_uri: str = lamda_write_to_s3(
        obj=cdr,
        prefix_stage="cdr",
        customer=customer,
        bucket_stage=BucketStage.PROCESS.value,
        date_from_event=date_from_event,
    )

    logger.info(f"CDR at S3 Processed {cdr_uri} --- ")

    recording: Recording = zoom_final.recording

    transcript: Transcript = zoom_final.transcript
    transcript_uri: str = lamda_write_to_s3(
        obj=transcript,
        prefix_stage="transcript",
        customer=customer,
        bucket_stage=BucketStage.PROCESS.value,
        date_from_event=date_from_event,
    )

    logger.info(f"Transcript at S3 Processed {transcript_uri} --- ")

    blob_id = str(zoom_final.cdr.source.source_id)
    obj_type = zoom_final.cdr.source.source_type

    zoom_final.cdr.source.source_id = cdr_uri  # CALL or MEET CDR at S3
    zoom_final.transcript.source.source_id = (
        transcript_uri  # CALL or MEET Transcription at S3
    )
    zoom_final.recording.source.source_id = (
        recording.download_url
    )  # CALL or MEET AUDIO at S3

    logger.info(f"Audio at S3 Processed {recording.download_url} --- ")

    processed_uri_path: str = lamda_write_to_s3(
        obj=zoom_final,
        prefix_stage=f"zoom_final_{obj_type}_{blob_id}",  # this is the final form ahead of ES parsing
        customer=customer,
        bucket_stage=BucketStage.PROCESS.value,
        date_from_event=date_from_event,
    )

    final_references: list = [blob_id, processed_uri_path]

    return zoom_final, final_references


def _get_todo_blob_ready_to_process(
    todo_ready_uri: str, s3_client: S3Helper
) -> ZoomDTO:
    logger.info(f"Loading {todo_ready_uri} for processing!")
    content_bucket: bytes = s3_client.get_file_content(todo_ready_uri)
    blob: dict = s3_client.to_json(content_bucket)
    return dataclass_wizard.fromdict(ZoomDTO, blob)
