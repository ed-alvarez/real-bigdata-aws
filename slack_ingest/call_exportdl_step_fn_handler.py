#!/usr/bin/env python
import json
import logging
import os
from datetime import datetime, timedelta

import aws_lambda_context
import aws_lambda_logging
import boto3
import settings

log_level = os.environ.get("LOGGING_LEVEL", "INFO")
boto_log_level = os.environ.get("BOTO_LOGGING_LEVEL", "INFO")
log = logging.getLogger()


def lambda_handler(event: dict, context: aws_lambda_context.LambdaContext) -> dict:
    # Purpose: Call Export Ingest Step Function with nice name via Boto3

    if os.environ.get("AWS_EXECUTION_ENV") is not None:
        aws_lambda_logging.setup(
            level=log_level,
            boto_level=boto_log_level,
            aws_request_id=context.aws_request_id,
            module="%(module)s",
        )

    now = datetime.now()
    now_as_str = now.strftime("%Y_%m_%d_%H_%M_%S")

    # Request should have client_name and date_y_m_d parameters
    if "date_y_m_d" not in event:
        # Call two days previous because undetermined what time Slack export will be ready, calling the export function directly without date_y_m_d parameter does this too.
        event["date_y_m_d"] = (now - timedelta(2)).strftime("%Y-%m-%d")

    nice_name = f'{event["client_name"]}-{event["date_y_m_d"]}-{now_as_str}'

    # Call Export Ingest Step Function with nice name via Boto3
    sf_client = boto3.client("stepfunctions")
    try:
        res = sf_client.start_execution(
            stateMachineArn=settings.EXPORTDL_STEP_FN_ARN,
            name=nice_name,
            input=json.dumps(event),
        )
    except Exception as e:
        log.exception(e)
        raise e

    log.info(f"response: {res}")
    return {"stepFunctionInvocation": nice_name}


if __name__ == "__main__":
    context: dict = {}
    request = {"client_name": "ips", "date_y_m_d": "2021-03-15"}
    lambda_handler(request, context)
