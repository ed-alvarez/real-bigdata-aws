import logging
import os

import aws_lambda_logging
import bbg_settings
from bbg_src.files_to_decode_lambda.files_to_decode import BBGFileDecode

log_level = bbg_settings.LOG_LEVEL
boto_log_level = bbg_settings.BOTO_LOG_LEVEL
log = logging.getLogger()

if os.environ.get("AWS_EXECUTION_ENV") is None:
    ch = logging.StreamHandler()
    log.addHandler(ch)


def lambda_handler(event, context):
    aws_lambda_logging.setup(level=log_level, boto_level=boto_log_level, aws_request_id=context.aws_request_id, module="%(module)s")
    log.info("Start File Decode")
    log.info('{"log_group_name" : "%s"}', context.log_group_name)
    log.info('{"log_stream_name" : "%s"}', context.log_stream_name)
    log.info('{"event" : "%s"}', event)

    files_to_decode = BBGFileDecode(event)
    result = files_to_decode.files_to_decode()

    log.info('{"result" : "%s"}', result)
    log.info("End File Decode")
    return result
