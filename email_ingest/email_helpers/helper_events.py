import datetime
import logging
import os
import pprint
import time
from urllib.parse import unquote_plus

from email_helpers.helper_paths import PathDetail, pathDetailSES
from email_settings import DONT_PROCESS_EMAIL_SUBJECT_LIST, eventType

log = logging.getLogger()
if os.environ.get("AWS_EXECUTION_ENV") is None:
    ch = logging.StreamHandler()
    log.addHandler(ch)


class EventDetail:
    def __init__(self):
        self._event = dict()
        self._destination = str("")
        self._client = str("")
        self._bucket = str("")
        self._message_id = str("")
        self._tmp_json_file = str("")
        self._path = str("")
        self._dynamo_db = False
        self._move_files = True
        self._event_type = None
        self._ingest_email_to_es = True
        self._ses_message_date = None

    @property
    def event(self):
        return self._event

    @event.setter
    def event(self, event):
        self._event = event
        self.update_atributes()

    @property
    def destination(self):
        return self._destination

    @property
    def client(self):
        return self._client

    @property
    def bucket(self):
        return self._bucket

    @property
    def message_id(self):
        return self._message_id

    @property
    def path(self):
        return self._path

    @property
    def dynamoDB(self):
        return self._dynamo_db

    @property
    def moveFiles(self):
        return self._move_files

    @property
    def IngestEmailToES(self):
        return self._ingest_email_to_es

    @property
    def sesMessageDate(self):
        return self._ses_message_date

    def return_client(self, bucket):
        client_decode = bucket.rsplit(".", 1)[0]
        if client_decode.split(".")[0] in ["todo", "stash", "archive"]:
            return client_decode.split(".")[1]
        else:
            return client_decode

    def set_es_processing_flag_subject(self, subject):
        block_list = DONT_PROCESS_EMAIL_SUBJECT_LIST
        if [item for item in block_list if (item in subject)]:
            log.warning(f"WARNING: Item with Subject {subject} will not be processed but will be archived")
            self._ingest_email_to_es = False
        else:
            self._ingest_email_to_es = True
        return

    def set_ses_message_date(self, message_date):
        try:
            t = time.strptime(message_date, "%a, %d %b %Y %H:%M:%S %z")
            self._ses_message_date = datetime.datetime.fromtimestamp(time.mktime(t))
        except ValueError:
            self._ses_message_date = datetime.datetime.now()
        return

    def update_atributes(self):
        if "ses" in self._event["Records"][0]:
            self._event_type = eventType.SES
            path_detail_obj = pathDetailSES()
            # Recpients is the Journaled email address NOT who the email is actually to.
            self._destination = self._event["Records"][0]["ses"]["receipt"]["recipients"][0]
            self._client = self._destination.split("@")[0]
            self._bucket = self._client.lower() + ".ips"  # shouldn't be hardcoded
            # Message ID maps to the name of the file in S3
            self._message_id = self._event["Records"][0]["ses"]["mail"]["messageId"]
            if "subject" in self._event["Records"][0]["ses"]["mail"]["commonHeaders"]:
                message_subject = self._event["Records"][0]["ses"]["mail"]["commonHeaders"]["subject"]
            else:
                message_subject = ""
            self.set_es_processing_flag_subject(subject=message_subject)
            message_date = self._event["Records"][0]["ses"]["mail"]["commonHeaders"]["date"]
            self.set_ses_message_date(message_date)
            path_detail_obj.messageID = self._message_id
            path_detail_obj.inputBucket = self._bucket
            path_detail_obj.eventType = self._event_type
            path_detail_obj.moveFiles = self._move_files
            path_detail_obj.ses_generate_key()
            path_detail_obj.generate_paths()

            self._path = path_detail_obj
            log.debug('{"destination" : "%s"}', self._destination)
            self._dynamo_db = True

        elif "s3" in self._event["Records"][0]:
            self._event_type = eventType.S3
            self._bucket = self._event["Records"][0]["s3"]["bucket"]["name"]
            self._client = self.return_client(self._bucket)
            extracted_key = unquote_plus(self._event["Records"][0]["s3"]["object"]["key"])
            full_path = os.path.split(extracted_key)
            self._message_id = full_path[1]
            path_detail_obj = PathDetail()
            path_detail_obj.inputKey = extracted_key
            path_detail_obj.inputBucket = self._bucket
            path_detail_obj.eventType = self._event_type
            path_detail_obj.moveFiles = self._move_files
            path_detail_obj.generate_paths()
            self._path = path_detail_obj

        else:
            self._event_type = eventType.Lambda
            self._bucket = self._event["Records"][0]["bucket"]
            self._client = self.return_client(self._bucket)
            extracted_key = unquote_plus(self._event["Records"][0]["key"])
            if "move_files" not in self._event["Records"][0]:
                self._move_files = False
            full_path = os.path.split(extracted_key)
            self._message_id = full_path[1]
            path_detail_obj = PathDetail()
            path_detail_obj.inputKey = extracted_key
            path_detail_obj.inputBucket = self._bucket
            path_detail_obj.eventType = self._event_type
            path_detail_obj.moveFiles = self._move_files
            path_detail_obj.generate_paths()
            self._path = path_detail_obj

        log.debug('{"client" : "%s"}', self._client)
        log.debug('{"bucket" : "%s"}', self._bucket)
        log.debug('{"_message_id" : "%s"}', self._message_id)
        log.debug('{"key" : "%s"}', self._path.processedKey)


if __name__ == "__main__":
    from email_ingest.email_tests.ses_records.s3_event import create_event as s3_event

    def test_helper_obj():
        MIME_MESSAGE = "01l55t21r5d74tpftq1o5bl1j9tikqfb44fovc81"
        lambda_event = s3_event(event_bucket="todo.ips.ips", event_key=f"email/01l55t21r5d74tpftq1o5bl1j9tikqfb44fovc81")
        helper_obj = EventDetail()
        helper_obj.event = lambda_event
        pprint.pprint(helper_obj.client)

    test_helper_obj()
