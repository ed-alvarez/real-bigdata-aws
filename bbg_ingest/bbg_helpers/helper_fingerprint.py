"""
Class for Fingerprint Meta Data to be inserted into the JSON message
"""

import logging
from datetime import datetime

from bbg_helpers.es_bbg_msg_index import fingerprint_meta

log = logging.getLogger()

META_ATTACHMENT = "fingerprint.attachments"


class FingerprintHelper:
    def __init__(self):
        self.fingerprint_meta_data = fingerprint_meta()
        self.msg_type = None
        self.str_msg_time = None
        self.client_name = None
        self.bucket_name = None
        self.key_name = None
        self.processed_time = None
        self.attachment_info = None
        self.attachment_key = None
        self.json_key = None
        self.schema = None

    def __repr__(self):
        return self.fingerprint_meta_data

    def set_schema(self, schema):
        self.create_key(schema=schema)
        self.schema = schema

    def set_msg_type(self, msg_type):
        self.create_key(type=msg_type)
        self.msg_type = msg_type

    def set_json_key(self, json_key):
        self.create_key(json_key=json_key)
        self.json_key = json_key

    def remove_json_key(self):
        if self.json_key:
            del self.fingerprint_meta_data["fingerprint.json_key"]
            self.json_key = None

    # def set_attachment_info(self, attachment_key, attachment_info):
    #     key_attachment_key = 'attachment_' + attachment_key
    #     kwargs = {}
    #     kwargs[key_attachment_key] = attachment_info
    #     self.create_key(**kwargs)
    #     self.attachment_info = attachment_info
    #     self.attachment_key = attachment_key

    # def remove_set_attachment_info(self):
    #     if self.attachment_key:
    #         search_attachment_key = 'fingerprint.' + self.attachment_key
    #         search_str = 'fingerprint.attachment_'
    #         original_keys = list(self.fingerprint_meta_data.keys())
    #         for key in original_keys:
    #             if search_str in key:
    #                 self.attachment_info = None
    #                 self.attachment_key = None
    #                 del self.fingerprint_meta_data[key]

    def set_attachment_info(self, attachment_key, attachment_info):
        attachments = self.fingerprint_meta_data.get(META_ATTACHMENT, {})
        attachments[attachment_key] = attachment_info
        self.fingerprint_meta_data[META_ATTACHMENT] = attachments
        self.attachment_info = attachment_info
        self.attachment_key = attachment_key

    def remove_set_attachment_info(self):
        try:
            del self.fingerprint_meta_data[META_ATTACHMENT]
        except Exception:
            pass

    def set_processed_time(self, processed_time=None):
        datetime_processed_time = datetime.now()
        if processed_time:
            datetime_processed_time = processed_time()
        es_str_processed_time = datetime_processed_time.strftime("%Y-%m-%d %H:%M:%S")
        self.create_key(processed_time=es_str_processed_time)
        self.processed_time = processed_time

    def set_msg_time(self, msg_time):
        datetime_msg_time = datetime.now()
        if self.msg_type == "bbg.msg":
            datetime_msg_time = datetime.strptime(str(msg_time), "%Y-%m-%d %H:%M:%S")
        elif self.msg_type == "bbg.im":
            datetime_msg_time = datetime.strptime(str(msg_time), "%m/%d/%Y %H:%M:%S")
        es_str_msg_time = datetime_msg_time.strftime("%Y-%m-%d %H:%M:%S")
        self.create_key(time=es_str_msg_time)
        self.str_msg_time = es_str_msg_time

    def set_client_name(self, client_name):
        self.create_key(client=client_name)
        self.client_name = client_name

    def set_bucket_name(self, bucket_name):
        self.create_key(bucket=bucket_name)
        self.bucket_name = bucket_name

    def set_key_name(self, key_name):
        self.create_key(key=key_name)
        self.key_name = key_name

    def create_key(self, **kwargs):
        if kwargs is not None:
            for key, value in kwargs.items():
                # fp_key = 'fingerprint.' + str(key)
                fp_key = str(key)
                setattr(self.fingerprint_meta_data, fp_key, value)
