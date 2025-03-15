import os
from pathlib import Path

import pytest
from bbg_src.ib_upload_lambda import parse_ib_xml_file
from bbg_src.ib_upload_lambda.bbg_ib_conversation import process_single_conversation
from bbg_src.ib_upload_lambda.ib_upload import ParseBBGXMLtoES
from mock import patch

BASE_DIR = Path(__file__).resolve().parent.parent


class mock_s3Helper:
    def __init__(self, bucketname: str, clientname: str):
        self.bucketName: str = bucketname
        self.clientName: str = clientname


mock_s3_helper_obj = mock_s3Helper(bucketname="testing.ips", clientname="testing")


class TestFunctions:
    tarFileName = f"{BASE_DIR}/fixtures/2020-03-16/decoded/f848135.att.200316.tar.gz"
    tar_file_contents = open(tarFileName, "rb").read()
    ib_file_name = f"{BASE_DIR}/fixtures/bbg_ib/ib_file_short.ib.200316.xml"
    ib_file_contents = open(ib_file_name, "rb").read()

    def test_xml_step_loop_timeout(self, test_lambda_context):
        test_lambda_context.time_limit_in_seconds = 900
        parse_ib_xml_obj: ParseBBGXMLtoES = ParseBBGXMLtoES(
            ib_FileName=TestFunctions.ib_file_name,
            ib_FileContents=TestFunctions.ib_file_contents,
            awsContext=test_lambda_context,
            xmlRecordNumber=0,
            tar_FileName=TestFunctions.tarFileName,
            tar_FileContents=TestFunctions.tar_file_contents,
            S3_helper=mock_s3_helper_obj,
        )
        with patch.object(process_single_conversation, "IB_UPLOAD_TO_ES", False):
            with patch.object(parse_ib_xml_file, "IB_AWS_TIMEOUT_MILLISECONDS", 90000000):
                parse_ib_xml_obj.initialise_variables()
                parse_ib_xml_obj.xml_step()
        assert parse_ib_xml_obj.xmlParseComplete is False
        assert parse_ib_xml_obj.xmlItemNextStart == 1

    def test_xml_step_loop_finish_sucessfully(self, test_lambda_context):
        test_lambda_context.time_limit_in_seconds = 900
        parse_ib_xml_obj: ParseBBGXMLtoES = ParseBBGXMLtoES(
            ib_FileName=TestFunctions.ib_file_name,
            ib_FileContents=TestFunctions.ib_file_contents,
            awsContext=test_lambda_context,
            xmlRecordNumber=0,
            tar_FileName=TestFunctions.tarFileName,
            tar_FileContents=TestFunctions.tar_file_contents,
            S3_helper=mock_s3_helper_obj,
        )
        with patch.object(process_single_conversation, "IB_UPLOAD_TO_ES", False):
            parse_ib_xml_obj.initialise_variables()
            parse_ib_xml_obj.xml_step()

        assert parse_ib_xml_obj.xmlParseComplete is True
        assert parse_ib_xml_obj.xmlItemNextStart == 4


class TestBugs:
    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_kirkoswold_many_attachments(self, test_lambda_context):
        tarFileName = f"{BASE_DIR}/bugs/f886973.ib19.att.210713.tar.gz"
        tar_file_contents = open(tarFileName, "rb").read()
        ib_file_name = f"{BASE_DIR}/bugs/f886973.ib19.210713.xml"
        ib_file_contents = open(ib_file_name, "rb").read()
        parse_ib_xml_obj: ParseBBGXMLtoES = ParseBBGXMLtoES(
            ib_FileName=ib_file_name,
            ib_FileContents=ib_file_contents,
            awsContext=test_lambda_context,
            xmlRecordNumber=0,
            tar_FileName=tarFileName,
            tar_FileContents=tar_file_contents,
            S3_helper=mock_s3_helper_obj,
        )
        with patch.object(process_single_conversation, "IB_UPLOAD_TO_ES", False):
            parse_ib_xml_obj.initialise_variables()
            parse_ib_xml_obj.xml_step()
        assert parse_ib_xml_obj.xmlParseComplete is True
        assert parse_ib_xml_obj.xmlItemNextStart == 830
