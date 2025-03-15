# local test of zoom_extract_blobs.pyl
from zoom_functions.zoom_extract_blobs import lambda_handler
from aws_lambda_powertools.utilities.typing import LambdaContext
import logging

logger = logging.getLogger()


class Context(LambdaContext):
    aws_request_id = ""


context = Context()

input_json_custom = {
    "customer": "dev-melqart",
    "ingest_range": "daily",
    "if_error": "",
    "start_date": "2022-11-24",
    "end_date": "2022-11-25",
    "bucket_name": "todo",
    "success_step": True,
    "done_workflow": False,
    "calls": [],
    "meets": [
        [87005238245, "hhOLO8WkT0yDkdmnWGmWsQ=="],
        [81215689109, "dli/21VLSdaqbEwn//VWJA=="],
        [88006051036, "/BPyQJxxShOt+fceANQ1mg=="],
    ],
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
