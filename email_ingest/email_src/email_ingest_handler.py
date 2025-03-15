""""
    Receive an SQS s3 _event notification new email message (object).  Process to json, save file and pass to SQS queue
    for uploading
    https://hackernoon.com/simple-steps-to-avoid-the-retry-behavior-from-aws-lambda-su4w63yx9
"""
import logging

import aws_lambda_logging
import email_settings
from elasticsearch.exceptions import ConflictError
from email_helpers.helper_dynamodb import emailDynamoDB
from email_helpers.helper_events import EventDetail
from email_helpers.helper_ses import processSESEvent
from email_helpers.helper_upload_to_es import UploadToElasticsearch
from email_src.email_ingest_process import MIMEConvert

log_level = email_settings.LOG_LEVEL
boto_log_level = email_settings.BOTO_LOG_LEVEL

log = logging.getLogger()


# if os.environ.get("AWS_EXECUTION_ENV") is None:
#    ch = logging.StreamHandler()
#    log.addHandler(ch)


# https://docs.aws.amazon.com/AmazonS3/latest/dev/notification-content-structure.html


def lambda_handler(event, context, s3_client=None):
    aws_lambda_logging.setup(level=log_level, boto_level=boto_log_level, aws_request_id=context.aws_request_id, module="%(module)s")

    response = None

    try:
        log.debug("Start email MIME To ES")
        log.info(event)
        response = ingest_email(event, context, s3_client)

        log.debug("End email MIME To ES")

    except Exception as error:
        response = {
            "status": 500,
            "error": {
                "type": type(error).__name__,
                "description": str(error),
            },
        }
        log.exception(response)

    finally:

        return response


def ingest_email(event, context, s3_client):
    event_obj: EventDetail = EventDetail()
    event_obj.event = event

    if event_obj.dynamoDB and email_settings.DYNAMO_DB:
        # Store Summary record in DynamoDB for billing
        # Convert Record to Dict
        record = processSESEvent()
        record.event = event
        record.parseEvent()

        # Upload Record to Dynamo DB  If it already exists then stop the lambda
        dynamo = emailDynamoDB()
        dynamo.dbRecord = record.dynamoRec
        dynamo.put_record()

    # Setup Email parsing class
    m2j_email_ingest = MIMEConvert(event_object=event_obj, context=context, s3_client=s3_client)
    m2j_email_ingest.setup_fingerprint_metadata()
    m2j_email_ingest.convert_MIME_to_dict()

    if email_settings.MOVE_FILES and event_obj.moveFiles:
        log.debug("Move file to archive")
        m2j_email_ingest.move_file_to_archive()

    if email_settings.ES_UPLOAD and event_obj.IngestEmailToES:
        log.debug("Upload to elasticSearch")
        elastic_upload = UploadToElasticsearch()
        log.debug("Load Email Obj to Upload Class")
        elastic_upload.emailDict = m2j_email_ingest.emailESObj

        # Set the ES_ID if the lambda is launched from an SES event
        if event_obj.message_id:
            elastic_upload.esId = event_obj.message_id
        log.debug("Do ES Upload")
        try:
            elastic_upload.do_upload()
        except ConflictError as ex:
            log.warning("Email is already in elasticsearch so will process the file move")
            pass

    if email_settings.MOVE_FILES and event_obj.moveFiles:
        log.debug("Move file to proccessed dir")
        m2j_email_ingest.move_file_to_processed()
        log.debug("Delete initial file")
        m2j_email_ingest.delete_initial_file()

    return True
