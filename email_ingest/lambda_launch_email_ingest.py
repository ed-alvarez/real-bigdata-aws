import boto3
import botocore
from botocore.stub import ANY, Stubber
from mock import patch

from email_ingest.email_src.email_ingest_handler import lambda_handler
from email_ingest.email_tests.ses_records.ses_event import create_event as ses_event

MIME_MESSAGE = "sample_MIME"

# records = test_event(event_bucket="stash.mirabella.ips",
#                   event_key = f"email/2016-11-16/njn5o4pio297hu56iga7lu4tcm2e00a0vtjfdi01")
# records = s3_event(event_bucket="stash.mirabella.ips",
#                   event_key = f"email/2016-11-16/{MIME_MESSAGE}rqcvpvpbpcq3sm5tbc5lvnh81")

records = ses_event(
    event_recipient="ips@ip-sentinel.net",
    event_message_id=f"{MIME_MESSAGE}rqcvpvpbpcq3sm5tbc5lvnh81",
    event_subject="HierarchySync_Ping_",
)

# records = ses_record1.aws_data_complex_meeting['Records']


class lambda_launch_email_ingest:
    class LambdaContext:
        def __init__(self):
            self.log_group_name = "local_test_log_group_name"
            self.log_stream_name = "local_test_log_stream_name"
            self.aws_request_id = "local_test_aws_request_id"

    @staticmethod
    def read_mime_file(file_id):
        mime_file_to_open = open("email_tests/sample_emails/" + str(file_id), "rb")
        msg = mime_file_to_open.read()
        return msg

    def __init__(self):
        self.context = self.LambdaContext()
        self.lambda_event = records

        self.orig = botocore.client.BaseClient._make_api_call

        # self.mime_file = self.read_mime_file(MIME_MESSAGE)
        self.mime_file = open("email_tests/sample_emails/" + MIME_MESSAGE, "rb")
        self.etag = '"example0etag"'
        self.stub_s3_get_object_response = {"Body": self.mime_file}
        self.stub_s3_get_object_params = {"Bucket": ANY, "Key": ANY}
        self.stub_s3_upload_file_response = {"ETag": self.etag, "ResponseMetadata": {"HTTPStatusCode": 200}}
        self.stub_s3_upload_file_params = {"Bucket": ANY, "Key": ANY, "Body": ANY}
        self.stub_s3_copy_object_response = {"VersionId": "string"}
        self.stub_s3_copy_object_params = {"Bucket": ANY, "Key": ANY, "CopySource": ANY}
        self.stub_s3_delete_object_params = {"Bucket": ANY, "Key": ANY}
        self.stub_s3_delete_object_response = {"VersionId": "string"}

    def mock_make_api_call(self, operation_name, kwarg):
        if operation_name == "GetObject":
            return {"Body": self.mime_file}
        elif operation_name == "PutObjectTagging":
            return {"VersionId": "string"}
        elif operation_name == "PutObject":
            return {"VersionId": "string"}
        else:
            return self.orig(self, operation_name, kwarg)

    @patch("email_settings.DYNAMO_DB", False)
    @patch("email_settings.ES_UPLOAD", True)
    @patch("email_settings.MOVE_FILES", True)
    @patch.object(boto3, "client")
    def lambda_launch(self, mock_client):
        stubbed_client = botocore.session.get_session().create_client("s3")
        stubber = Stubber(stubbed_client)
        stubber.add_response("get_object", self.stub_s3_get_object_response, self.stub_s3_get_object_params)
        stubber.add_response("copy_object", self.stub_s3_copy_object_response, self.stub_s3_copy_object_params)
        stubber.add_response("copy_object", self.stub_s3_copy_object_response, self.stub_s3_copy_object_params)
        stubber.add_response("delete_object", self.stub_s3_delete_object_response, self.stub_s3_delete_object_params)
        stubber.add_response("delete_object", self.stub_s3_delete_object_response, self.stub_s3_delete_object_params)
        # stubber.add_client_error(method='get_object',
        #                         service_error_code='NoSuchKey',
        #                         service_message='The specified key does not exist.',
        #                         http_status_code=404)
        stubber.activate()
        mock_client.return_value = stubbed_client
        # calendar_mock.side_effect = ValueError()
        # bs4_mock.side_effect = ValueError()

        # with patch('botocore.client.BaseClient._make_api_call', new=self.mock_make_api_call):
        lambda_handler(self.lambda_event, self.context)


if __name__ == "__main__":

    lambda_result = lambda_launch_email_ingest()
    lambda_result.lambda_launch()
