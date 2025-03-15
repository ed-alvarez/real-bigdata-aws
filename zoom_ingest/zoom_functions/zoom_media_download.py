import logging
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

import aws_lambda_logging
import dataclass_wizard
from aws_lambda_powertools.utilities.typing import LambdaContext

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))  # for any host run-time
sys.path.append(str(tenant_directory))

from zoom_settings import BOTO_LOG_LEVEL, LOG_LEVEL
from zoom_shared.api_media import MediaController
from zoom_shared.zoom_dataclasses import ZoomFilesTracker
from zoom_shared.zoom_utils import (
    error_handler,
    pending_raw_blob_call,
    pending_raw_blob_meet,
    update_if_error,
)

logger = logging.getLogger()

# ENHANCE MEDIA DOWNLOAD_URL WITH S3_URI DOWNLOADED MP3/M4A


@error_handler
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict:
    """
    Input
    {
        "customer": "melqart",
        "ingest_range": "daily"
        "bucket_name": "todo",
        "success_step": False,
        "done_workflow": False,
        "calls": [raw_call_blob_URI, ... ],
        "meets": [raw_meet_blob_URI, ...]
    }

    Output
    {
        "customer": "melqart",
        "date_range": "daily",
        "bucket_name": "todo.zoom",
        "success_step": True,
        "done_workflow": False,
        "calls": [call_blob_URI, ... ],
        "meets": [meet_blob_URI, ...]
    }
    """

    aws_lambda_logging.setup(
        level=LOG_LEVEL,
        boto_level=BOTO_LOG_LEVEL,
        aws_request_id=context.aws_request_id,
        module="%(module)s",
    )

    zoom_event_bus: ZoomFilesTracker = validate_event_payload(event=event)
    result: ZoomFilesTracker = download_media(zoom_event_bus)

    return result.to_json()


def validate_event_payload(event: Dict[str, Any]) -> ZoomFilesTracker:
    event = dataclass_wizard.fromdict(ZoomFilesTracker, event)
    event.if_error = {}
    return event


@update_if_error
def download_media(zoom_event_bus: ZoomFilesTracker) -> ZoomFilesTracker:
    zoom_event_bus.success_step = False
    logger.info(f"Checking {asdict(zoom_event_bus)} for media to download")

    call_blob_to_enhance = pending_raw_blob_call(zoom_event_bus.calls)
    meet_blob_to_enhance = pending_raw_blob_meet(zoom_event_bus.meets)

    logger.debug(
        f"Zoom Downloading Media for URIs: {call_blob_to_enhance} | {meet_blob_to_enhance}"
    )

    if call_blob_to_enhance or meet_blob_to_enhance:
        api_media_controller = MediaController(zoom_event_bus)

        if call_blob_to_enhance:
            api_media_controller.enhance_blob_call(call_blob_to_enhance)

        if meet_blob_to_enhance:
            api_media_controller.enhance_blob_meet(meet_blob_to_enhance)

        zoom_event_bus: ZoomFilesTracker = api_media_controller.step_tracker
    else:
        zoom_event_bus.success_step = True

    return zoom_event_bus
