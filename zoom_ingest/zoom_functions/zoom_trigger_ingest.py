import logging
import sys
from pathlib import Path

import aws_lambda_logging
from aws_lambda_powertools.utilities.typing import LambdaContext

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))  # for any host run-time
sys.path.append(str(tenant_directory))

from typing import Any, Dict

from zoom_settings import BOTO_LOG_LEVEL, LOG_LEVEL, SF_ARN
from zoom_shared.zoom_dataclasses import LaunchIngestChannel, ZoomEvent

from shared.shared_src.sf.launch_step import LaunchStepFunction

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict:
    """
    {
        "customer": "ips",
        "tenant": "zoom",
        "ingest_range": "daily" | "historical"
        "tenant_ssm_secret_A": "123",
        "tenant_ssm_secret_B": "345"
        ...
        "tenant_ssm_secret_N": "567"
    }
    """
    response: Dict = {}

    aws_lambda_logging.setup(
        level=LOG_LEVEL,
        boto_level=BOTO_LOG_LEVEL,
        aws_request_id=context.aws_request_id,
        module="%(module)s",
    )

    try:
        logger.info(f"Triggering Zoom State machine: {event}")
        launch_step_function: LaunchStepFunction = LaunchStepFunction(
            event, stateMachineArn=SF_ARN
        )
        step_fn_name: str = launch_step_function.start_execution_step_function(
            LaunchIngestChannel, ZoomEvent
        )

        response = {"statusCode": 200, "body": step_fn_name}

    except Exception as error:
        response = {
            "statusCode": 500,
            "body": {
                "type": type(error).__name__,
                "description": str(error),
            },
        }
        logger.exception(error)
        logger.error("End with Error Zoom Step Function")

    finally:
        return response


# AWS local trigger test
class Context(LambdaContext):
    aws_request_id = ""


context = Context()

step_fn_launch_event_daily = (
    {  # no need for diff payload at event-bridge vs. state machine trigger event
        "customer": "melqart",
        "ingest_range": "daily",
    }
)


step_fn_launch_event_historical = {
    "customer": "melqart",
    "ingest_range": "custom",
    "start_date": "2022-11-24",
    "end_date": "2022-11-25",
}

logger.info(lambda_handler(event=step_fn_launch_event_historical, context=context))
