import logging

import aws_lambda_logging
import bbg_settings
from bbg_src.step_function_launch.launch_step import LaunchStepFunction

log_level = bbg_settings.LOG_LEVEL
boto_log_level = bbg_settings.BOTO_LOG_LEVEL
log = logging.getLogger()


def lambda_handler(event, context):
    aws_lambda_logging.setup(level=log_level, boto_level=boto_log_level, aws_request_id=context.aws_request_id, module="%(module)s")
    response = {}
    try:
        log.info(event)
        launch_step_function = LaunchStepFunction(event)
        lambda_response = launch_step_function.Launch_Step_Function()
        response = {"statusCode": 200, "body": lambda_response}

    except Exception as error:
        response = {
            "statusCode": 500,
            "body": {
                "type": type(error).__name__,
                "description": str(error),
            },
        }
        log.exception(error)
        log.error("End with Error BBG Step Function")

    finally:
        return response
