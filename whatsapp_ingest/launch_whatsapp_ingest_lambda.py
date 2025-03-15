from datetime import datetime, timedelta

import boto3
import botocore
from botocore.stub import ANY, Stubber
from mock import patch

from whatsapp_ingest.whatsapp_src.whatsapp_handler import lambda_handler
from whatsapp_ingest.whatsapp_tests.emails import message_event
from whatsapp_ingest.whatsapp_tests.events.s3_event import create_event


class lambda_launch_whatsapp_ingest:
    class TestLambdaContext:
        def __init__(self, time_limit_in_seconds=120):
            self.log_group_name = "local_test_log_group_name"
            self.log_stream_name = "local_test_log_stream_name"
            self.aws_request_id = "local_test_aws_request_id"

            self.start_time = datetime.now()
            self.time_limit_in_seconds = time_limit_in_seconds
            self.end_time = self.start_time + timedelta(seconds=self.time_limit_in_seconds)

        def get_remaining_time_in_millis(self):
            time_now = datetime.now()
            if time_now <= self.end_time:
                time_left = self.end_time - time_now
                time_left_milli = (time_left.seconds * 1000) + (time_left.microseconds / 1000)
            else:
                time_left_milli = 0
            return int(time_left_milli)

    def __init__(self):
        self.context = self.TestLambdaContext()
        self.aws_event = dict()
        self.orig = botocore.client.BaseClient._make_api_call

        self.file_name = str()
        self.file = None
        self.stub_msg = None

        self.stub_s3_get_object_params = {"Bucket": ANY, "Key": ANY}

    @property
    def event(self):
        return self.aws_event

    @event.setter
    def event(self, aws_event):
        self.aws_event = aws_event

    @property
    def fileName(self):
        return self.file_name

    @fileName.setter
    def fileName(self, file_name):
        self.file_name = file_name
        self.generate_s3_stub()

    def generate_s3_stub(self):
        self.file = open("whatsapp_tests/emails/" + self.file_name, "rb")

        self.stub_msg = {"Body": self.file}

        self.stub_s3_get_object_params = {"Bucket": ANY, "Key": ANY}
        self.stub_s3_copy_object_response = {"VersionId": "string"}
        self.stub_s3_copy_object_params = {"Bucket": ANY, "Key": ANY, "CopySource": ANY}
        self.stub_s3_delete_object_params = {"Bucket": ANY, "Key": ANY}
        self.stub_s3_delete_object_response = {"VersionId": "string"}

    @patch("settings.DYNAMO_DB", False)
    @patch.object(boto3, "client")
    def lambda_launch(self, mock_client):

        stubbed_client = botocore.session.get_session().create_client("s3")
        stubber = Stubber(stubbed_client)
        stubber.add_response("get_object", self.stub_msg, self.stub_s3_get_object_params)
        # stubber.add_client_error(method='get_object',
        #                         service_error_code='NoSuchKey',
        #                         service_message='The specified key does not exist.',
        #                         http_status_code=404)
        stubber.add_response("copy_object", self.stub_s3_copy_object_response, self.stub_s3_copy_object_params)
        stubber.add_response("copy_object", self.stub_s3_copy_object_response, self.stub_s3_copy_object_params)
        stubber.add_response("delete_object", self.stub_s3_delete_object_response, self.stub_s3_delete_object_params)
        stubber.activate()
        mock_client.return_value = stubbed_client

        lambda_handler(self.aws_event, self.context)


if __name__ == "__main__":
    test_event = message_event.test_with_picture
    event = create_event(event_bucket=test_event["bucket"], event_key=test_event["key"])
    lambda_result = lambda_launch_whatsapp_ingest()
    lambda_result.event = event
    lambda_result.fileName = test_event["name"]
    lambda_result.lambda_launch()
