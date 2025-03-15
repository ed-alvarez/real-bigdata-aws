import logging
from datetime import datetime
from typing import Dict

from aws_lambda_context import LambdaContext

from whatsapp_ingest import whatsapp_settings as settings
from whatsapp_ingest.whatsapp_helpers.es_whatsapp_index import (
    WHATSAPP,
    Fingerprint_Meta,
    Schema,
)
from whatsapp_ingest.whatsapp_helpers.helper_objects import (
    newEventDetail,
    newPathDetail,
)
from whatsapp_ingest.whatsapp_helpers.helper_s3 import S3Object
from whatsapp_ingest.whatsapp_helpers.helper_upload_to_es import UploadToElasticsearch
from whatsapp_ingest.whatsapp_src.whatsapp_decode import whatsappParser

log = logging.getLogger()


class WhatsappConvert:
    def __init__(self, event: Dict, context: LambdaContext) -> None:
        self._event: Dict = event
        self._context: LambdaContext = context
        self._event_obj: newEventDetail = newEventDetail(event=self._event)
        self._path_obj: newPathDetail = newPathDetail(message_id=self._event_obj.message_id)
        self._s3_obj = S3Object(event_object=self._event_obj)
        self._fingerprint_metadata: Fingerprint_Meta = Fingerprint_Meta()
        self._esWHATSAPP = WHATSAPP()

    def setup_fingerprint_metadata(self, event_obj: newEventDetail, context: LambdaContext) -> Fingerprint_Meta:
        fingerprint_meta: Fingerprint_Meta = Fingerprint_Meta()
        fingerprint_meta.client = event_obj.client
        fingerprint_meta.bucket = event_obj.bucket
        fingerprint_meta.type = settings.MSG_TYPE
        fingerprint_meta.processed_time = datetime.now()
        fingerprint_meta.aws_lambda_id = context.aws_request_id
        fingerprint_meta.ses_message_id = event_obj.message_id
        fingerprint_meta.schema = Schema.version
        return fingerprint_meta

    def get_file_from_s3(self):
        log.debug("Ingest Whatsapp started...")

        # Get the MIME message email body for processing
        try:
            log.debug("Preparing to create s3_helper Class")
            self._s3_obj.collect_object(file_key=self._path_obj.key)
        except Exception as ex:
            log.error(ex)
            raise

    def convert_whatsapp_email_to_es_object(self) -> WHATSAPP:
        self._fingerprint_metadata = self.setup_fingerprint_metadata(event_obj=self._event_obj, context=self._context)

        parser = whatsappParser(email_body=self._s3_obj.emailBody, fingerprint_meta=self._fingerprint_metadata)
        parser.parse_email_to_es_whatsapp()

        self._esWHATSAPP = parser.esWhatsApp

        # Set the date on the path object now we know the date of the message
        self._path_obj.set_date(date_time=self._esWHATSAPP.date)

        self._path_obj.set_root_folder(settings.S3_BUCKET_PROCESSED)

        # Update the Fingerprint Meta with the path
        self._esWHATSAPP.fingerprint.key = self._path_obj.dated_key

        return parser.esWhatsApp

    def upload_message_to_es(self):
        log.debug("Upload to elasticSearch")
        elastic_upload = UploadToElasticsearch()
        elastic_upload.whatsappObj = self._esWHATSAPP
        try:
            elastic_upload.do_upload()
        except Exception as ex:
            log.exception(ex)
            raise
        return

    def move_file_to_archive(self):
        self._path_obj.set_root_folder(settings.S3_BUCKET_TODO)
        src_key: str = self._path_obj.key
        self._path_obj.set_root_folder(settings.S3_BUCKET_ARCHIVED)
        dst_key: str = self._path_obj.dated_key
        try:
            # move mime files to dated processed and archive folders; copy json files to processed (leaving original for next step in pipeline)
            self._s3_obj.copy_file_between_folders(src_key=src_key, dst_key=dst_key)
        except Exception as ex:
            log.exception(ex)
            raise

    def move_file_to_processed(self):
        self._path_obj.set_root_folder(settings.S3_BUCKET_TODO)
        src_key: str = self._path_obj.key
        self._path_obj.set_root_folder(settings.S3_BUCKET_PROCESSED)
        dst_key: str = self._path_obj.dated_key
        try:
            # move mime files to dated processed and archive folders; copy json files to processed (leaving original for next step in pipeline)
            self._s3_obj.copy_file_between_folders(src_key=src_key, dst_key=dst_key)

        except Exception as ex:
            log.exception(ex)
            raise

    def delete_initial_file(self):
        self._path_obj.set_root_folder(settings.S3_BUCKET_TODO)
        key: str = self._path_obj.key
        try:
            self._s3_obj.delete_file(key=key)
        except Exception as ex:
            log.exception(ex)
            raise
