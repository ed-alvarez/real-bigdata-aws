# Local execution of zoom_create_ids.py
from zoom_functions import lambda_handler
from aws_lambda_powertools.utilities.typing import LambdaContext
import logging

logger = logging.getLogger()


class Context(LambdaContext):
    aws_request_id = ""


context = Context()

input_json_custom = {"customer": "dev-melqart", "ingest_range": "daily"}

logger.info(lambda_handler(event=input_json_custom, context=context))
