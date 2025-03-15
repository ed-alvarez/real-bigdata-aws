import logging
import sys
from pathlib import Path
from typing import Any, Dict

import aws_lambda_logging
from aws_lambda_powertools.utilities.typing import LambdaContext

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_settings import BOTO_LOG_LEVEL, LOG_LEVEL, SF_ARN, STAGE
from teams_src.teams_shared_modules.step_funtion_data_classes import LaunchIngestChannel

from shared.shared_src.sf.launch_step import LaunchStepFunction
from shared.shared_src.sf.step_function_client import StepFunctionOrchestrator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# one execution at the time, to avoid time-outs.
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict:
    response: Dict = {}

    aws_lambda_logging.setup(
        level=LOG_LEVEL,
        boto_level=BOTO_LOG_LEVEL,
        aws_request_id=context.aws_request_id,
        module="%(module)s",
    )

    try:
        logger.info(f"Triggering Teams State machine: {event}")
        launch_step_function: LaunchStepFunction = LaunchStepFunction(event, state_machine_arn=SF_ARN)
        step_fn_name, execution_arn = launch_step_function.start_execution_step_function(LaunchIngestChannel)
        logger.info(f"{step_fn_name} triggered with {event}")
        response = {"statusCode": 200, "step_fn_name": step_fn_name, "execution_arn": execution_arn}

    except Exception as error:
        response = {
            "statusCode": 500,
            "body": {
                "type": type(error).__name__,
                "description": str(error),
            },
        }
        logger.exception(error)
        logger.error("End with Error Teams Step Function")

    return response
