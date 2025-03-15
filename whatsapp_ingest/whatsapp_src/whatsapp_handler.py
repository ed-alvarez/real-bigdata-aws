""""
    Recieve an SES event with a Whatsapp SMTP and process
    https://hackernoon.com/simple-steps-to-avoid-the-retry-behavior-from-aws-lambda-su4w63yx9
"""
import logging
from typing import Dict

import aws_lambda_logging

# from whatsapp_helpers.helper_ses import processSESEvent
# from whatsapp_helpers.helper_dynamodb import emailDynamoDB
from aws_lambda_context import LambdaContext

from whatsapp_ingest import whatsapp_settings
from whatsapp_ingest.whatsapp_src.whatsapp_ingest_utils import WhatsappConvert

log_level = whatsapp_settings.LOG_LEVEL
boto_log_level = whatsapp_settings.BOTO_LOG_LEVEL

log = logging.getLogger()


def lambda_handler(event, context):
    aws_lambda_logging.setup(level=log_level, boto_level=boto_log_level, aws_request_id=context.aws_request_id, module="%(module)s")

    response = None

    try:
        log.info("Start WhatsApp ingest")
        log.info(event)
        response = ingest_email(event, context)

        log.info("End WhatsApp ingest")

    except Exception as error:
        log.error(error)
        error_type = error.__class__.__name__
        try:
            error_status_code = error.status_code
            error_error = error_status_code["error"]
            error_description = f'{error_error["type"]} {error_error["reason"]}'
        except:
            error_description = error

        finally:
            if not error_description:
                error_description = "Unknown Error Reason"

        response = {
            "status": 500,
            "error": {
                "type": error_type,
                "description": error_description,
            },
        }

        log.info(response)
        log.info("End Whatsapp Ingest")

    finally:
        return response


def ingest_email(event: Dict, context: LambdaContext):
    # if settings.DYNAMO_DB:
    # Store Summary record in DynamoDB for billing
    # Convert Record to Dict
    #    record = processSESEvent()
    #    record.event = event
    #    record.parseEvent()

    # Upload Record to Dynamo DB  If it already exists then stop the lambda
    #    dynamo = emailDynamoDB()
    #    dynamo.dbRecord = record.dynamoRec
    #    dynamo.put_record()

    # Setup Email parsing class
    whatsapp_ingest = WhatsappConvert(event=event, context=context)

    try:
        whatsapp_ingest.get_file_from_s3()
    except Exception as ex:
        raise

    try:
        whatsapp_ingest.convert_whatsapp_email_to_es_object()
    except Exception as ex:
        raise

    if whatsapp_settings.UPLOAD_TO_ES:
        log.debug("Upload to ElasticSearch")
        try:
            whatsapp_ingest.upload_message_to_es()
        except Exception as ex:
            raise

    if whatsapp_settings.MOVE_FILES:
        log.debug("Move file to archive")
        whatsapp_ingest.move_file_to_archive()
        log.debug("Move file to proccessed dir")
        whatsapp_ingest.move_file_to_processed()
        log.debug("Delete initial file")
        whatsapp_ingest.delete_initial_file()

    return True
