"""
python -m unittest -v mime_to_json_lambda/email_tests/helper_objects_tests.py
"""

import datetime

from email_helpers.helper_events import EventDetail
from email_helpers.helper_paths import PathDetail, pathDetailSES
from email_settings import eventType
from email_tests.event_data import records


class TestEventObject:
    def test_Event_Detail(self):
        event = records
        event_obj = EventDetail()
        event_obj.event = event
        assert event_obj.client == "melqart"
        assert event_obj.destination == "melqart@ip-sentinel.net"
        assert event_obj.bucket == "melqart.ips"
        assert event_obj.message_id == "1k9bqt4574vl85vhquc5ecc92fpa44tca8e8pcg1"


file_name = "testmessageid"
folder_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
test = dict()
test["bucket"] = "todo.ips.ips"
test["key"] = "dev.processed.email/2020-04-03/mime/" + file_name


class TestPathObject:
    def test_ses_path(self):
        path_detail = pathDetailSES()
        path_detail.messageID = file_name
        path_detail.inputBucket = "ips.ips"
        path_detail.eventType = eventType.SES
        path_detail.ses_generate_key()
        path_detail.generate_paths()
        assert path_detail.archivedKey == f"dev.archived.email/{folder_date}/mime/testmessageid"
        assert path_detail.processedBucket == "ips.ips"
        assert path_detail.processedKey == f"dev.processed.email/{folder_date}/mime/testmessageid"

    def test_s3_and_event_path_move_false(self):
        path_detail = PathDetail()
        path_detail.inputKey = test["key"]
        path_detail.inputBucket = test["bucket"]
        path_detail.eventType = eventType.S3
        path_detail.moveFiles = False
        path_detail.generate_paths()
        assert path_detail.processedBucket == "todo.ips.ips"
        assert path_detail.archivedKey == ""
        assert path_detail.processedKey == "dev.processed.email/2020-04-03/mime/testmessageid"

    def test_s3_and_event_path_move_true(self):
        path_detail = PathDetail()
        path_detail.inputKey = test["key"]
        path_detail.inputBucket = test["bucket"]
        path_detail.eventType = eventType.S3
        path_detail.moveFiles = True
        path_detail.generate_paths()
        assert path_detail.processedBucket == "ips.ips"
        assert path_detail.archivedKey == f"dev.archived.email/{folder_date}/mime/testmessageid"
        assert path_detail.processedKey == f"dev.processed.email/{folder_date}/mime/testmessageid"

    def test_s3_and_event_path_move_true_with_email_date(self):
        path_detail = PathDetail()
        path_detail.inputKey = test["key"]
        path_detail.inputBucket = test["bucket"]
        path_detail.set_path_date_from_email(datetime.datetime(2012, 1, 1, 10, 10, 10))
        path_detail.eventType = eventType.S3
        path_detail.moveFiles = True
        path_detail.generate_paths()
        assert path_detail.processedBucket == "ips.ips"
        assert path_detail.archivedKey == "dev.archived.email/2012-01-01/mime/testmessageid"
        assert path_detail.processedKey == "dev.processed.email/2012-01-01/mime/testmessageid"
