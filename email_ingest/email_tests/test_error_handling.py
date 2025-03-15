from pathlib import Path
from unittest.mock import patch

import boto3
import botocore
import pytest
from botocore.stub import ANY, Stubber
from email_helpers.helper_fingerprint import FingerprintHelper
from email_src.email_ingest_handler import lambda_handler
from email_src.email_utils.individual_email_process import EMAILObject
from email_tests.ses_records import ses_record1
from icalendar import Calendar

BASE_DIR = Path(__file__).resolve().parent.parent


class TestErrorEmailHandler:
    @staticmethod
    def mime_file(file_id):
        mime_file_to_open = open(f"{BASE_DIR}/email_tests/sample_emails/" + str(file_id), "rb")
        msg = mime_file_to_open.read()
        return msg

    class FingerPrintMeta:
        def __init__(self):
            self.fingerprint_metadata = FingerprintHelper()
            self.fingerprint_metadata.clientName = "test"
            self.fingerprint_metadata.key_name = "123456789"
            self.fingerprint_metadata.bucket_name = "test.ips"
            self.fingerprint_metadata.msg_type = "email"
            self.fingerprint_metadata.processedTime = None

    @patch.object(Calendar, "from_ical")
    def test_from_ical_error(self, mock_calendar):
        mock_calendar.side_effect = ValueError()

        mime_file_id = "complex_meeting"
        email = EMAILObject()
        email.byteMail = self.mime_file(file_id=mime_file_id)
        response = email.process_message()
        assert "Warning - Unable to decode Calendar Item" in email.email.body
        assert response is True

    @patch("email_src.email_utils.email_payload.BeautifulSoup")
    def test_decode_html_error(self, mock_BS4):
        mock_BS4.side_effect = ValueError()
        mime_file_id = "sample_MIME_HTML_only"
        email = EMAILObject()
        email.byteMail = self.mime_file(file_id=mime_file_id)
        response = email.process_message()
        assert "Warning - Unable to decode HTML Body of email" in email.email.body
        assert response is True

    @patch("email_src.email_utils.generate_email_obj.from_string")
    def test_cannot_unpack_email(self, mock_BytesParser):
        mock_BytesParser.side_effect = ValueError()

        mime_file_id = "complex_meeting"
        email = EMAILObject()
        email.byteMail = self.mime_file(file_id=mime_file_id)

        with pytest.raises(Exception) as e:
            assert email.process_message()
        assert "Raw Email String load Fail" in str(e.value)


class TestControlModuleErrors:
    class LambdaContext:
        def __init__(self):
            self.log_group_name = "local_test_log_group_name"
            self.log_stream_name = "local_test_log_stream_name"
            self.aws_request_id = "local_test_aws_request_id"

    class SetupRun:
        def __init__(self, file_id):
            records = ses_record1.aws_data_complex_meeting["Records"]
            self.context = TestControlModuleErrors.LambdaContext()
            self.ses_event = {}
            self.ses_event["Records"] = records

            self.orig = botocore.client.BaseClient._make_api_call
            self.mime_file = open(f"{BASE_DIR}/email_tests/sample_emails/" + file_id, "rb")
            self.etag = '"example0etag"'
            self.stub_s3_get_object_response = {"Body": self.mime_file}
            self.stub_s3_get_object_params = {"Bucket": ANY, "Key": ANY}
            self.stub_s3_upload_file_response = {
                "ETag": self.etag,
                "ResponseMetadata": {"HTTPStatusCode": 200},
            }
            self.stub_s3_upload_file_params = {"Bucket": ANY, "Key": ANY, "Body": ANY}
            self.stub_s3_copy_object_response = {"VersionId": "string"}
            self.stub_s3_copy_object_params = {"Bucket": ANY, "Key": ANY, "CopySource": ANY}
            self.stub_s3_delete_object_params = {"Bucket": ANY, "Key": ANY}
            self.stub_s3_delete_object_response = {"VersionId": "string"}

    @patch.object(boto3, "client")
    def test_lambda_launch(self, mock_client):
        mime_file_id = "complex_meeting"
        params = self.SetupRun(file_id=mime_file_id)
        stubbed_client = botocore.session.get_session().create_client("s3")
        stubber = Stubber(stubbed_client)
        stubber.add_response("get_object", params.stub_s3_get_object_response, params.stub_s3_get_object_params)
        stubber.add_response("put_object", params.stub_s3_upload_file_response, params.stub_s3_upload_file_params)
        stubber.add_response("copy_object", params.stub_s3_copy_object_response, params.stub_s3_copy_object_params)
        stubber.add_response("copy_object", params.stub_s3_copy_object_response, params.stub_s3_copy_object_params)
        stubber.add_response("copy_object", params.stub_s3_copy_object_response, params.stub_s3_copy_object_params)
        stubber.add_response("delete_object", params.stub_s3_delete_object_response, params.stub_s3_delete_object_params)
        stubber.activate()
        mock_client.return_value = stubbed_client
        return_value = lambda_handler(params.ses_event, params.context)

        assert return_value["status"] == 500

    @patch.object(boto3, "client")
    def test_fail_to_find_email_object_in_s3_bucket(self, mock_client):
        mime_file_id = "complex_meeting"
        params = self.SetupRun(file_id=mime_file_id)
        stubbed_client = botocore.session.get_session().create_client("s3")
        stubber = Stubber(stubbed_client)
        stubber.add_client_error(
            method="get_object",
            service_error_code="NoSuchKey",
            service_message="The specified key does not exist.",
            http_status_code=404,
        )
        mock_client.return_value = stubbed_client
        return_value = lambda_handler(params.ses_event, params.context)
        assert return_value["status"] == 500

    @patch("email_src.email_utils.individual_email_process.EMAILObject")
    @patch.object(boto3, "client")
    def test_email_decodes_properly(self, mock_client, mock_email_decode):
        mime_file_id = "complex_meeting"
        params = self.SetupRun(file_id=mime_file_id)
        stubbed_client = botocore.session.get_session().create_client("s3")
        stubber = Stubber(stubbed_client)
        stubber.add_response("get_object", params.stub_s3_get_object_response, params.stub_s3_get_object_params)
        stubber.add_response("put_object", params.stub_s3_upload_file_response, params.stub_s3_upload_file_params)
        stubber.activate()
        mock_client.return_value = stubbed_client
        mock_email_decode.side_effect = ValueError()
        return_value = lambda_handler(params.ses_event, params.context)
        assert return_value["status"] == 500
