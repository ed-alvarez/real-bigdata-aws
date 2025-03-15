"""
Class for Fingerprint Meta Data to be inserted into the JSON message
"""

import logging
from datetime import datetime

from email_helpers.es_email_index_v2 import Fingerprint_Meta, Schema

log = logging.getLogger()


class FingerprintHelper:
    def __init__(self):
        self._fingerprint_meta_data = Fingerprint_Meta()
        self._msg_type = None
        self._msg_time = None
        self._client_name = None
        self._bucket_name = None
        self._key_name = None
        self._processed_time = None
        self.attachment_info = None
        self.attachment_key = None
        self._json_key = None
        self._aws_lambda_id = None
        self._ses_message_id = None
        self._datetime_msg_time = None
        self._schema = Schema.version
        self.create_key(schema=self._schema)

    def __repr__(self):
        return self._fingerprint_meta_data

    @property
    def fingerprintMetaData(self):
        return self._fingerprint_meta_data

    @property
    def schemaVersion(self):
        return self._schema

    @property
    def msgType(self):
        return self._msg_type

    @msgType.setter
    def msgType(self, msg_type):
        self._msg_type = msg_type
        self.create_key(type=self._msg_type)

    @property
    def awsLambdaID(self):
        return self._aws_lambda_id

    @awsLambdaID.setter
    def awsLambdaID(self, aws_lambda_id):
        self._aws_lambda_id = aws_lambda_id
        self.create_key(aws_lambda_id=self._aws_lambda_id)

    @property
    def jsonKey(self):
        return self._json_key

    @jsonKey.setter
    def jsonKey(self, json_key):
        self._json_key = json_key
        self.create_key(json_key=self._json_key)

    @jsonKey.deleter
    def jsonKey(self, json_key):
        if self._json_key:
            del self._fingerprint_meta_data[json_key]
            self._json_key = None

    @property
    def processedTime(self):
        return self._processed_time

    @processedTime.setter
    def processedTime(self, processed_time=None):
        datetime_processed_time = datetime.now()
        if processed_time:
            datetime_processed_time = processed_time()
        # es_str_processed_time = datetime_processed_time.strftime("%Y-%m-%d %H:%M:%S")
        es_str_processed_time = datetime_processed_time
        self._processed_time = es_str_processed_time
        self.create_key(processed_time=self._processed_time)

    @property
    def msgTime(self):
        return self._msg_time

    @msgTime.setter
    def msgTime(self, msg_time):
        if msg_time:
            self._msg_time = msg_time
        else:
            self._msg_time = datetime.now()

        self.create_key(time=self._msg_time)

    @property
    def clientName(self):
        return self._client_name

    @clientName.setter
    def clientName(self, client_name):
        self._client_name = client_name
        self.create_key(client=self._client_name)

    @property
    def bucketName(self):
        return self._bucket_name

    @bucketName.setter
    def bucketName(self, bucket_name):
        self._bucket_name = bucket_name
        self.create_key(bucket=self._bucket_name)

    @property
    def keyName(self):
        return self._key_name

    @keyName.setter
    def keyName(self, key_name):
        self._key_name = key_name
        self.create_key(key=self._key_name)

    @property
    def sesMessageId(self):
        return self._ses_message_id

    @sesMessageId.setter
    def sesMessageId(self, ses_message_id):
        self._ses_message_id = ses_message_id
        self.create_key(ses_message_id=self._ses_message_id)

    def create_key(self, **kwargs):
        if kwargs is not None:
            for key, value in kwargs.items():
                log.debug(f"set fingerprint key: {str(key)}, with value {value}")
                self._fingerprint_meta_data[str(key)] = value
