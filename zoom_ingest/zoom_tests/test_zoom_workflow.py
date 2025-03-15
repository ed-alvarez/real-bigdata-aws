import logging
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, Union

import aws_lambda_logging
from aws_lambda_powertools.utilities.typing import LambdaContext

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))  # for any host run-time
sys.path.append(str(tenant_directory))

from zoom_ingest.zoom_functions.zoom_create_ids import lambda_handler as create
from zoom_ingest.zoom_functions.zoom_extract_blobs import lambda_handler as extract
from zoom_ingest.zoom_functions.zoom_media_download import lambda_handler as download
from zoom_ingest.zoom_functions.zoom_process import lambda_handler as process

# THIS IS TO LOCALLY TEST THE STATE MACHINE WORKFLOW LAMBDAS
# Eventually to become integration testing(?)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Context(LambdaContext):
    aws_request_id = ""


context = Context()

input_json_custom = {
    "customer": "dev-melqart",
    "period": "custom",
    "start_date": "2022-11-24",
    "end_date": "2022-11-25",
}

create_input_payload = {
    "customer": "dev-melqart",
    "period": "custom",
    "if_error": {},
    "start_date": "2022-11-24",
    "end_date": "2022-11-25",
    "bucket_name": "todo",
    "success_step": True,
    "done_workflow": False,
    "calls": [
        "35553f5e-59e7-4b49-9970-17e16d47dfdb",
        "05d0353e-4f34-4acc-99ee-830f5df12d84",
        "e922eb69-8d2f-442f-a8c8-1d5ca278f9fc",
        "79dbc944-dc31-4bef-aa19-6a93d02d047e",
    ],
    "meets": [
        [87005238245, "hhOLO8WkT0yDkdmnWGmWsQ=="],
        [88006051036, "/BPyQJxxShOt+fceANQ1mg=="],
        [84065432222, "aiaR1KSbSfuY25fTmDuqoA=="],
        [81215689109, "dli/21VLSdaqbEwn//VWJA=="],
    ],
}

# create_input_payload = create(event=input_json_custom, context=context)
logger.info(f"First Event#1: {create_input_payload}")

for _ in range(len(create_input_payload["meets"])):
    extract_input_payload = extract(event=create_input_payload, context=context)
    logger.info(f"Second Event#2: {extract_input_payload}")

    download_input_payload = download(event=extract_input_payload, context=context)
    logger.info(f"Third Event#3: {download_input_payload}")

    process_input_payload = process(event=download_input_payload, context=context)
    logger.info(f"Forth Event#4: {process_input_payload}")
