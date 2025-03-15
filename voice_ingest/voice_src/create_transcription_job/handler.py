import logging

import aws_lambda_logging
import voice_settings
from voice_src.create_transcription_job.transcribe import transcribeVoice

log_level = voice_settings.LOG_LEVEL
boto_log_level = voice_settings.BOTO_LOG_LEVEL
log = logging.getLogger()


def lambda_handler(event, context):
    aws_lambda_logging.setup(level=log_level, boto_level=boto_log_level, aws_request_id=context.aws_request_id, module="%(module)s")

    response = None

    try:
        log.info("Start Transcribe Audio")
        log.info(event)
        obj_transcribe_voice: transcribeVoice = transcribeVoice(event=event)
        response = obj_transcribe_voice.process_event()

        log.info("End Transcribe Audio")

    except Exception as error:
        response = {
            "status": 500,
            "error": {
                "type": type(error).__name__,
                "description": str(error),
            },
        }
        log.error(response)
        log.error("End with Error Transcribe Audio")

    finally:

        return response

    return True
