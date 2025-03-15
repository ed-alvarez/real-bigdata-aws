# local test of zoom_process.py
from zoom_functions.zoom_process import lambda_handler
from aws_lambda_powertools.utilities.typing import LambdaContext
import logging

logger = logging.getLogger()


class Context(LambdaContext):
    aws_request_id = ""


context = Context()

input_json_custom = {
    "customer": "dev-melqart",
    "ingest_range": "custom",
    "if_error": {},
    "start_date": "2022-10-14",
    "end_date": "2022-10-16",
    "bucket_name": "todo",
    "success_step": True,
    "done_workflow": False,
    "calls": [],
    "meets": [
        "todo.zoom/2022-10-21/ready_meet_qc+vymeZR2KMkqqu8mECsQ==_1669295974770.json"
    ],
}

logger.info(
    lambda_handler(
        event=lambda_handler(event=input_json_custom, context=context), context=context
    )
)
