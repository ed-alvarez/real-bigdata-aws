"""
Lambda function to drive BBG parsing and upload to elasticsearch
"""

import logging
import os
from dataclasses import asdict

from bbg_helpers import helper_file
from bbg_helpers.helper_dataclass import BbgFiles, DecodeLambdaParameters
from bbg_src.msg_upload_lambda.parse_msg_xml_file import ParseBBGXMLtoES
from elasticsearch import exceptions

from shared.shared_src.s3.s3_helper import S3Helper

log_level = os.environ.get("LOGGING_LEVEL", "INFO")
boto_log_level = os.environ.get("BOTO_LOGGING_LEVEL", "INFO")
log = logging.getLogger()


class MSGUpload:
    def __init__(self, event):
        self._event = event
        self._lambda_parameters = DecodeLambdaParameters(**self._event)
        if "bbg_files" in self._event:
            self._bbg_params = BbgFiles(**self._event["bbg_files"])
            self._lambda_parameters.bbg_files = self._bbg_params

    def msg_uploaded(self, context):
        log.debug("BBG MSG Upload {}".format(self._event))
        result = {}

        s3_obj: S3Helper = S3Helper(client_name=self._lambda_parameters.client_name, ingest_type="bbg")
        xml_record_number = self._bbg_params.MSG_XML_record_number

        bbg_archive_file_location: str = ""

        # If the ATT file exists download it to TMP
        if self._bbg_params.MSG_ATT_file_name:
            attachments_file = self._bbg_params.MSG_ATT_file_name
            obj_attachments_file = helper_file.FileHelper(attachments_file)
            tar_file_bytes: bytes = s3_obj.get_file_content(file_key=obj_attachments_file.file)
            bbg_archive_file_location = obj_attachments_file.tmp_file

        # Download the MSG XML file to /TMP
        file_to_process = self._bbg_params.MSG_file_name
        obj_file_to_process = helper_file.FileHelper(file_to_process)
        msg_xml_file_bytes: bytes = s3_obj.get_file_content(file_key=obj_file_to_process.file)

        # Process XML and upload it to ES
        obj_convert: ParseBBGXMLtoES = ParseBBGXMLtoES(
            msg_FileContents=msg_xml_file_bytes,
            msg_FileName=file_to_process,
            tar_FileContents=tar_file_bytes,
            tar_FileName=attachments_file,
            awsContext=context,
            xmlMessageNumber=xml_record_number,
            S3_helper=s3_obj,
        )

        obj_convert.initialise_variables()
        log.info("Start Convert processing %s", obj_file_to_process.tmp_file)
        try:
            obj_convert.xml_step()
        except exceptions.ElasticsearchException as ex:
            log.exception(ex)
            raise ex
        log.info("Finished Convert processing %s", obj_file_to_process.tmp_file)

        if obj_convert.xmlParseComplete:
            self._bbg_params.MSG_XML_to_process = False
        else:
            self._bbg_params.MSG_XML_to_process = True
            self._bbg_params.MSG_XML_record_number = obj_convert.xmlItemNextStart

        return asdict(self._lambda_parameters)


if __name__ == "__main__":
    from datetime import datetime, timedelta

    import boto3
    from botocore import session
    from botocore.stub import ANY, Stubber
    from mock import patch

    from bbg_ingest.bbg_tests import step_case_MSG

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

    class TestStepWrapper:
        @patch("settings.UPLOAD_TO_ES", False)
        @patch.object(boto3, "client")
        def loop(self, mock_client, event, context):
            xml_file_name = "/bbg_tests/fixtures_new/2020-03-16/decoded/f848135.msg.200316.xml"
            xml_file = open(xml_file_name, "rb")

            stub_msg_xlm = {"Body": xml_file}

            tar_file_name = "/bbg_tests/fixtures_new/2020-03-16/decoded/f848135.att.200316.tar.gz"
            tar_file = open(tar_file_name, "rb")
            stub_tar_xml = {"Body": tar_file}

            stub_s3_get_object_params = {"Bucket": ANY, "Key": ANY}

            stubbed_client = session.get_session().create_client("s3")
            stubber = Stubber(stubbed_client)
            stubber.add_response("get_object", stub_msg_xlm, stub_s3_get_object_params)
            stubber.add_response("get_object", stub_tar_xml, stub_s3_get_object_params)
            stubber.activate()
            mock_client.return_value = stubbed_client

            msg_upload = MSGUpload(event["input"])
            response = msg_upload.msg_uploaded(context)

            print(response)
            print(type(response))

            return response

        def test_loop_1(self):
            event = step_case_MSG.setup_input_message(MSG_XML_No=1)
            context = TestLambdaContext(time_limit_in_seconds=10)

            response = self.loop(event=event, context=context)

    test = TestStepWrapper()
    test.test_loop_1()
