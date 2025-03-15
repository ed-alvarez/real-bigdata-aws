import logging
import os
import shutil

import aws_lambda_logging
from bbg_src.msg_upload_lambda.msg_upload import MSGUpload

log_level = os.environ.get("LOGGING_LEVEL", "INFO")
boto_log_level = os.environ.get("BOTO_LOGGING_LEVEL", "INFO")
log = logging.getLogger()


def lambda_handler(event, context):
    if os.environ.get("AWS_EXECUTION_ENV") is None:
        ch = logging.StreamHandler()
        log.addHandler(ch)
        aws_lambda_logging.setup(level=log_level, boto_level=boto_log_level, module="%(module)s")
    else:
        aws_lambda_logging.setup(
            level=log_level,
            boto_level=boto_log_level,
            aws_request_id=context.aws_request_id,
            module="%(module)s",
        )

    if os.environ.get("AWS_EXECUTION_ENV") is None:
        temp_dir = "tmp"
    else:
        temp_dir = "/tmp"

    for root, dirs, files in os.walk(temp_dir):
        for f in files:
            try:
                os.unlink(os.path.join(root, f))
            except Exception:
                pass
        for d in dirs:
            try:
                shutil.rmtree(os.path.join(root, d))
            except Exception:
                pass
    response = None
    try:
        log.info("Start File To JSON")
        log.info(event)

        msg_upload = MSGUpload(event)
        response = msg_upload.msg_uploaded(context)

        log.info(response)
        log.info("End File To JSON")

    except Exception as error:
        #
        response = {
            "status": 500,
            "error": {
                "type": type(error).__name__,
                "description": str(error),
            },
        }
        log.error(response)
        log.error("End with Error BBG MSG Parse & Upload")

    finally:
        return response
