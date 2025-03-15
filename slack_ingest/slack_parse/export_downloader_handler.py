#!/usr/bin/env python
import logging
import os

import aws_lambda_context
import aws_lambda_logging
import slack_parse.download_export.slack_export_downloader as sed

log_level = os.environ.get("LOGGING_LEVEL", "INFO")
boto_log_level = os.environ.get("BOTO_LOGGING_LEVEL", "INFO")
log = logging.getLogger()


def lambda_handler(event: dict, context: aws_lambda_context.LambdaContext) -> dict:
    if os.environ.get("AWS_EXECUTION_ENV") is not None:
        aws_lambda_logging.setup(
            level=log_level,
            boto_level=boto_log_level,
            aws_request_id=context.aws_request_id,
            module="%(module)s",
        )

    # Request should have client_name and date_y_m_d parameters
    res = sed.download_from_lambda_event(event)
    print(res)
    return res


if __name__ == "__main__":
    context: dict = {}
    request = {"client_name": "ips", "date_y_m_d": "2021-03-15"}
    lambda_handler(request, context)
