# Local testing of the zoom_media_download lambda function

from zoom_functions.zoom_media_download import lambda_handler
from aws_lambda_powertools.utilities.typing import LambdaContext
import logging

logger = logging.getLogger()


class Context(LambdaContext):
    aws_request_id = ""


context = Context()

input_json_custom = {
    "customer": "melqart",
    "ingest_range": "custom",
    "if_error": "",
    "start_date": "2022-11-10",
    "end_date": "2022-11-11",
    "bucket_name": "todo",
    "success_step": True,
    "done_workflow": False,
    "calls": [
        "todo.zoom/2022-11-22/raw_call_4b6aba89-c7cc-4986-a8d1-c6f571bc56c8_1669148203650.json"
    ],
    "meets": [],
}


logger.info(
    lambda_handler(
        event=lambda_handler(
            event=lambda_handler(
                event=lambda_handler(event=input_json_custom, context=context),
                context=context,
            ),
            context=context,
        ),
        context=context,
    )
)
