from contextlib import contextmanager
from pathlib import Path

from bbg_src.msg_upload_lambda import parse_msg_xml_file
from bbg_src.msg_upload_lambda.msg_upload import MSGUpload
from bbg_tests.fixtures.StepfnIO.msg_ib_step_message import setup_msg_ib_step_message
from mock import patch

CLIENT_NAME = "testing"
BUCKET_NAME = f"{CLIENT_NAME}.ips"
BASE_DIR = Path(__file__).resolve().parent.parent


class TestFunctions:
    @contextmanager
    def s3_setup(self, s3_client):
        bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": "eu-west-1"})

        IB_tar_key = "dev.todo.bbg/2020-03-16/decoded/f848135.att.200316.tar.gz"
        IB_tar_location = f"{BASE_DIR}/fixtures/2020-03-16/decoded/f848135.att.200316.tar.gz"
        with open(IB_tar_location, "rb") as f:
            s3_client.upload_fileobj(f, BUCKET_NAME, IB_tar_key)

        yield

    def test_process_full_file_processed(self, s3_client, test_lambda_context):
        test_input_event = setup_msg_ib_step_message(client_name=CLIENT_NAME)
        test_lambda_context.time_limit_in_seconds = 900

        with patch.object(parse_msg_xml_file, "UPLOAD_TO_ES", False):
            with self.s3_setup(s3_client):
                MSG_file_key = "dev.todo.bbg/2020-03-16/decoded/f848135.msg.200316.xml"
                MSG_file_location = f"{BASE_DIR}/fixtures/bbg_msg/msg_file_short.msg.200316.xml"
                with open(MSG_file_location, "rb") as f:
                    s3_client.upload_fileobj(f, BUCKET_NAME, MSG_file_key)

                ib_upload_obj = MSGUpload(event=test_input_event["input"])
                result = ib_upload_obj.msg_uploaded(test_lambda_context)

        assert result["bbg_files"]["MSG_XML_to_process"] is False

    def test_process_part_file_processed(self, s3_client, test_lambda_context):
        test_input_event = setup_msg_ib_step_message(client_name=CLIENT_NAME)
        test_lambda_context.time_limit_in_seconds = 900

        with patch.object(parse_msg_xml_file, "UPLOAD_TO_ES", False):
            with patch.object(parse_msg_xml_file, "MSG_AWS_TIMEOUT_MILLISECONDS", 6000000):
                with patch.object(parse_msg_xml_file, "MSG_EMAIL_BATCH_SIZE", 1):
                    with self.s3_setup(s3_client):
                        MSG_file_key = "dev.todo.bbg/2020-03-16/decoded/f848135.msg.200316.xml"
                        MSG_file_location = f"{BASE_DIR}/fixtures/bbg_msg/msg_file_short.msg.200316.xml"
                        with open(MSG_file_location, "rb") as f:
                            s3_client.upload_fileobj(f, BUCKET_NAME, MSG_file_key)

                        ib_upload_obj = MSGUpload(event=test_input_event["input"])
                        result = ib_upload_obj.msg_uploaded(test_lambda_context)

        assert result["bbg_files"]["MSG_XML_to_process"] is True
        assert result["bbg_files"]["MSG_XML_record_number"] == 2

    def test_process_intermediate_part_file_processed(self, s3_client, test_lambda_context):
        test_input_event = setup_msg_ib_step_message(client_name=CLIENT_NAME, MSG_XML_No=2)
        test_lambda_context.time_limit_in_seconds = 900

        with patch.object(parse_msg_xml_file, "UPLOAD_TO_ES", False):
            with patch.object(parse_msg_xml_file, "MSG_AWS_TIMEOUT_MILLISECONDS", 6000000):
                with patch.object(parse_msg_xml_file, "MSG_EMAIL_BATCH_SIZE", 3):
                    with self.s3_setup(s3_client):
                        MSG_file_key = "dev.todo.bbg/2020-03-16/decoded/f848135.msg.200316.xml"
                        MSG_file_location = f"{BASE_DIR}/fixtures/bbg_msg/msg_file_short.msg.200316.xml"
                        with open(MSG_file_location, "rb") as f:
                            s3_client.upload_fileobj(f, BUCKET_NAME, MSG_file_key)

                        ib_upload_obj = MSGUpload(event=test_input_event["input"])
                        result = ib_upload_obj.msg_uploaded(test_lambda_context)

        assert result["bbg_files"]["MSG_XML_to_process"] is True
        assert result["bbg_files"]["MSG_XML_record_number"] == 5

    def test_process_big_file_processed(self, s3_client, test_lambda_context):
        test_input_event = setup_msg_ib_step_message(client_name=CLIENT_NAME)
        test_lambda_context.time_limit_in_seconds = 900

        with patch.object(parse_msg_xml_file, "UPLOAD_TO_ES", False):
            with self.s3_setup(s3_client):
                MSG_file_key = "dev.todo.bbg/2020-03-16/decoded/f848135.msg.200316.xml"
                MSG_file_location = f"{BASE_DIR}/fixtures/bbg_msg/msg_file_short.msg.200316.xml"
                with open(MSG_file_location, "rb") as f:
                    s3_client.upload_fileobj(f, BUCKET_NAME, MSG_file_key)

                ib_upload_obj = MSGUpload(event=test_input_event["input"])
                result = ib_upload_obj.msg_uploaded(test_lambda_context)

        assert result["bbg_files"]["MSG_XML_to_process"] is False
