from logging import getLogger

from aws_lambda_logging import setup
from voice_settings import BOTO_LOG_LEVEL, LOG_LEVEL
from voice_src.process_transcript_job.process_transcript import ProcessTranscript

log = getLogger()


def lambda_handler(event, context):
    setup(level=LOG_LEVEL, boto_level=BOTO_LOG_LEVEL, aws_request_id=context.aws_request_id, module="%(module)s")

    response = None

    try:
        log.info("Start Process Transcript")
        log.info(event)
        process_transcript_obj = ProcessTranscript(event, context)
        response = process_transcript_obj.process_transcript()

        log.info("End Process Transcript")

    except Exception as error:
        response = {
            "status": 500,
            "error": {
                "type": type(error).__name__,
                "description": str(error),
            },
        }
        log.exception(response)
        log.error("End with Error Process Transcript")

    finally:

        return response
