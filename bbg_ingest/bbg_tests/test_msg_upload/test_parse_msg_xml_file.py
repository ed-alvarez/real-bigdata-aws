from pathlib import Path

from bbg_src.msg_upload_lambda import parse_msg_xml_file
from bbg_src.msg_upload_lambda.parse_msg_xml_file import ParseBBGXMLtoES
from mock import patch

BASE_DIR = Path(__file__).resolve().parent.parent

tarFileName = f"{BASE_DIR}/fixtures/2020-03-16/decoded/f848135.att.200316.tar.gz"
msg_file_name = f"{BASE_DIR}/fixtures/bbg_msg/msg_file_short.msg.200316.xml"
# msg_file_name = f'{BASE_DIR}/fixtures/2020-03-16/decoded/f848135.msg.200316.xml'

msg_file_contents = open(msg_file_name, "rb").read()
tar_file_contents = open(tarFileName, "rb").read()


class mock_s3Helper:
    def __init__(self, bucketname: str, clientname: str):
        self.bucketName: str = bucketname
        self.clientName: str = clientname


mock_s3_helper_obj = mock_s3Helper(bucketname="testing.ips", clientname="testing")


class TestFunctions:
    def test_xml_step_loop_timeout(self, test_lambda_context):
        test_lambda_context.time_limit_in_seconds = 1
        parse_msg_xml_obj: ParseBBGXMLtoES = ParseBBGXMLtoES(
            msg_FileName=msg_file_name,
            msg_FileContents=msg_file_contents,
            awsContext=test_lambda_context,
            xmlMessageNumber=0,
            tar_FileName=tarFileName,
            tar_FileContents=tar_file_contents,
            S3_helper=mock_s3_helper_obj,
        )
        with patch.object(parse_msg_xml_file, "UPLOAD_TO_ES", False):
            with patch.object(parse_msg_xml_file, "MSG_AWS_TIMEOUT_MILLISECONDS", 600000):
                with patch.object(parse_msg_xml_file, "MSG_EMAIL_BATCH_SIZE", 1):
                    parse_msg_xml_obj.initialise_variables()
                    parse_msg_xml_obj.xml_step()
        assert parse_msg_xml_obj.xmlParseComplete is False
        assert parse_msg_xml_obj.xmlItemNextStart == 2

    def test_xml_step_loop_finish_sucessfully(self, test_lambda_context):
        test_lambda_context.time_limit_in_seconds = 900
        parse_msg_xml_obj: ParseBBGXMLtoES = ParseBBGXMLtoES(
            msg_FileName=msg_file_name,
            msg_FileContents=msg_file_contents,
            awsContext=test_lambda_context,
            xmlMessageNumber=0,
            tar_FileName=tarFileName,
            tar_FileContents=tar_file_contents,
            S3_helper=mock_s3_helper_obj,
        )
        with patch.object(parse_msg_xml_file, "UPLOAD_TO_ES", False):
            parse_msg_xml_obj.initialise_variables()
            parse_msg_xml_obj.xml_step()

        assert parse_msg_xml_obj.xmlParseComplete is True
        assert parse_msg_xml_obj.xmlItemNextStart == 17
