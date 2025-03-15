import logging
import os
import shutil

import aws_lambda_logging
from bbg_src.ib_upload_lambda.ib_upload import IBUpload

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

    for root, dirs, files in os.walk("/tmp"):
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

        ib_upload = IBUpload(event)
        response = ib_upload.file_to_json(context)

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
        log.error("End with Error BBG IB Parse & Upload")

    finally:
        return response
