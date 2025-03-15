import os
from datetime import datetime, timedelta

import boto3
import botocore
from botocore.stub import ANY, Stubber
from elasticsearch import exceptions
from mock import patch

from bbg_ingest.bbg_src.msg_upload_lambda import msg_upload

if os.path.exists("tmp/f848135.att.200316.tar.gz"):
    os.remove("tmp/f848135.att.200316.tar.gz")

if os.path.exists("tmp/f848135.msg.200316.xml"):
    os.remove("tmp/f848135.msg.200316.xml")

bbg_files = {}
bbg_files["ATT_file_found"] = False
bbg_files["MSG_file_found"] = True
bbg_files["IB_file_found"] = False
bbg_files["ATT_file_name"] = ""
bbg_files["MSG_file_name"] = "todo.bbg/2020-06-18/decoded/f902504.msg.200618.xml"
bbg_files["MSG_XML_to_process"] = True
bbg_files["IB_file_name"] = ""
bbg_files["IB_XML_to_process"] = False
bbg_files["IB_XML_to_record_number"] = 0
bbg_files["MSG_json_file_number"] = 0

event = {}
event["file_to_process"] = "todo.bbg/2020-06-18/decoded/f902504.msg.200618.xml"
event["json_file_number"] = 0
event["xml_record_number"] = 0
event["attachments_file"] = ""
event["client_name"] = "melqart"
event["bbg_files"] = bbg_files


class LambdaContext:
    def __init__(self):
        self.log_group_name = "local_test_log_group_name"
        self.log_stream_name = "local_test_log_stream_name"
        self.aws_request_id = "local_test_aws_request_id"

        self.start_time = datetime.now()
        self.time_limit_in_mins = 2
        self.time_limit_in_seconds = self.time_limit_in_mins * 60
        self.end_time = self.start_time + timedelta(seconds=self.time_limit_in_seconds)

    def get_remaining_time_in_millis(self):
        time_now = datetime.now()
        if time_now <= self.end_time:
            time_left = self.end_time - time_now
        else:
            time_left = 3600000
        return time_left.seconds * 1000


context = LambdaContext()

os.environ["MSG_ES_BULK"] = "False"


class lambdalaunch:
    def __init__(self):

        self.orig = botocore.client.BaseClient._make_api_call

        self.xml_file_name = "f848135.msg.200316.xml"
        self.xml_file = open("bbg_tests/fixtures_new/2020-03-16/decoded/" + self.xml_file_name, "rb")

        self.stub_msg_xml = {"Body": self.xml_file}

        self.tar_file_name = "f848135.att.200316.tar.gz"
        self.tar_file = open("bbg_tests/fixtures_new/2020-03-16/decoded/" + self.tar_file_name, "rb")
        self.stub_tar_xml = {"Body": self.tar_file}

        self.stub_s3_get_object_params = {"Bucket": ANY, "Key": ANY}

    @patch("settings.UPLOAD_TO_ES", True)
    @patch.object(boto3, "client")
    def main(self, mock_client):
        stubbed_client = botocore.session.get_session().create_client("s3")
        stubber = Stubber(stubbed_client)
        stubber.add_response("get_object", self.stub_msg_xml, self.stub_s3_get_object_params)
        stubber.add_response("get_object", self.stub_tar_xml, self.stub_s3_get_object_params)
        stubber.activate()
        mock_client.return_value = stubbed_client

        try:
            # with patch('botocore.client.BaseClient._make_api_call', new=self.mock_make_api_call):
            msg_upload.lambda_handler(event, context)
        except exceptions.ElasticsearchException as ex:
            raise ex


if __name__ == "__main__":
    lambdatest = lambdalaunch()
    lambdatest.main()
