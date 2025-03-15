import logging
import time
from typing import List

import email_settings
from aws_embedded_metrics import metric_scope
from email_helpers.es_email_index_v2 import EMAIL
from email_helpers.helper_events import EventDetail
from email_helpers.helper_fingerprint import FingerprintHelper
from email_helpers.log_messages import error
from email_src.email_utils import individual_email_process

from shared.shared_src.s3.s3_helper import S3Helper

log = logging.getLogger()


class MIMEConvert:
    def __init__(self, event_object: EventDetail, context, s3_client):
        self._event_obj: EventDetail = event_object
        self._context = context
        self._json_text = None
        self._fingerprint_metadata = FingerprintHelper()
        self._email_es_obj = EMAIL()
        self._s3_client: S3Helper = S3Helper(
            client_name=self._event_obj.client, ingest_type=email_settings.INGEST_TYPE, s3_client=s3_client
        )

    @property
    def fingerprintMetadata(self):
        return self._fingerprint_metadata

    @property
    def emailESObj(self):
        return self._email_es_obj

    @emailESObj.setter
    def emailESObj(self, email_obj):
        self._email_es_obj = email_obj

    def setup_fingerprint_metadata(self):
        self._fingerprint_metadata.clientName = self._event_obj.client
        self._fingerprint_metadata.bucketName = self._event_obj.path.processedBucket
        self._fingerprint_metadata.msgType = email_settings.MSG_TYPE
        self._fingerprint_metadata.processedTime = None
        self._fingerprint_metadata.awsLambdaID = self._context.aws_request_id
        self._fingerprint_metadata.sesMessageId = self._event_obj.message_id

    @metric_scope
    def convert_MIME_to_dict(self, metrics):
        """
        Main processor function for parsing the message and returning a formatted dict.
        """
        log.debug("Mail processor started...")

        tries = 3
        sleep_sec = 5
        email_body: bytes = bytes()

        for i in range(tries):
            try:
                email_body = self._s3_client.get_file_body_with_utf_correction(file_key=self._event_obj.path.inputKey)
            except Exception as e:
                if i < tries - 1:  # i is zero indexed
                    log.warning(f"File not found, waiting {sleep_sec} to try again {e}")
                    time.sleep(sleep_sec)
                    continue
                else:
                    error_msg = error["file_not_found"].format(self._event_obj.path.inputKey, self._event_obj.path.inputBucket)
                    log.exception(error_msg)
                    raise Exception(error_msg)
            break
        # Get the MIME message email body for processing

        if self._event_obj.IngestEmailToES:
            # Decode the email body into useful data
            try:
                log.debug("Preparing to decode Message")
                email_obj = individual_email_process.EMAILObject()
                email_obj.byteMail = email_body
                email_obj.process_message()
                log.debug("Finished Decoding Message")

            except Exception:
                error_msg = error["message_not_processed"]
                log.exception(error_msg)
                raise Exception(error_msg)

            date = email_obj.email.date
            log.debug(f"set email date: {date} from envelope {email_obj.email.date}")
            log.debug("Update fingerprint meta with date")
            self._fingerprint_metadata.msgTime = date
            log.debug("Update object meta with date")
            self._event_obj.path.set_path_date_from_email(date_dt=self._fingerprint_metadata.msgTime)
            self._fingerprint_metadata.keyName = self._event_obj.path.processedKey

            # Update with Fingerprint metadata
            log.debug("add fingerprint metadata to es email record")
            email_obj.email.fingerprint = self.fingerprintMetadata.fingerprintMetaData

            log.debug("set class Final email object")
            self.emailESObj = email_obj.email

            metrics.put_metric("EmailProcessed", 1, "Count")
            metrics.set_namespace(f"email-{email_settings.STAGE.lower()}")
            metrics.put_dimensions({"firm": email_obj.email.fingerprint.client})

            return
        else:
            self._event_obj.path.set_path_date_from_email(date_dt=self._event_obj.sesMessageDate)

    def move_file_to_processed(self):
        try:
            if self._event_obj.IngestEmailToES:
                # move mime files to dated processed and archive folders; copy json files to processed (leaving original for next step in pipeline)
                self._s3_client.copy_file_between_folders(
                    src_key=self._event_obj.path.inputKey, dst_key=self._event_obj.path.processedKey
                )
            else:
                log.info(f"{self._event_obj.path.inputKey} is not being processed but will be archived")

        except Exception:
            error_msg = error["cannot_copy_MIME_to_s3_processed"].format(
                self._event_obj.path.inputKey, self._event_obj.path.processedKey
            )
            log.exception(error_msg)
            raise Exception(error_msg)

    def move_file_to_archive(self):

        try:
            # move mime files to dated processed and archive folders; copy json files to processed (leaving original for next step in pipeline)
            self._s3_client.copy_file_between_folders(src_key=self._event_obj.path.inputKey, dst_key=self._event_obj.path.archivedKey)

        except Exception:
            error_msg = error["cannot_copy_MIME_to_s3_archived"].format(
                self._event_obj.path.inputKey, self._event_obj.path.archivedKey
            )
            log.exception(error_msg)
            raise Exception(error_msg)

    def delete_initial_file(self):
        delete_list: List = []
        try:
            # Add directory key back in to delete
            delete_list.append({"Key": self._event_obj.path.inputKey})

            # Remove files from Origin
            self._s3_client.delete_list_of_objects(list_of_objects_to_delete=delete_list)

        except Exception:
            error_msg = error["cannot_delete_MIME_from_todo"].format(self._event_obj.path.inputKey)
            log.exception(error_msg)
            raise Exception(error_msg)
