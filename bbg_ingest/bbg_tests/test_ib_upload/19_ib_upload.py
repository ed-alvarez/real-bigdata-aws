from contextlib import contextmanager
from pathlib import Path

from bbg_src.ib_upload_lambda import parse_ib_xml_file
from bbg_src.ib_upload_lambda.bbg_ib_conversation import process_single_conversation
from bbg_src.ib_upload_lambda.ib_upload import IBUpload
from bbg_tests.fixtures.StepfnIO.msg_ib_step_message import setup_msg_ib_step_message
from mock import patch

CLIENT_NAME = "testing"
BUCKET_NAME = f"{CLIENT_NAME}.ips"
BASE_DIR = Path(__file__).resolve().parent.parent


class TestFunctions:
    @contextmanager
    def s3_setup(self, s3_client):
        bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": "eu-west-1"})

        IB_file_key = "dev.todo.bbg/2021-03-02/decoded/f908067.ib19.210302.xml"
        IB_file_location = f"{BASE_DIR}/fixtures/new_bbg/f908067.ib19.210302.xml"
        with open(IB_file_location, "rb") as f:
            s3_client.upload_fileobj(f, BUCKET_NAME, IB_file_key)

        IB_tar_key = "dev.todo.bbg/2021-03-12/decoded/f908067.ib19.att.210302.tar.gz"
        IB_tar_location = f"{BASE_DIR}/fixtures/new_bbg/f908067.ib19.att.210302.tar.gz"
        with open(IB_tar_location, "rb") as f:
            s3_client.upload_fileobj(f, BUCKET_NAME, IB_tar_key)

        yield

    def test_process_full_file_processed(self, s3_client, test_lambda_context):
        test_input_event = setup_msg_ib_step_message(client_name=CLIENT_NAME)
        test_lambda_context.time_limit_in_seconds = 9000

        with patch.object(process_single_conversation, "IB_UPLOAD_TO_ES", False):
            with patch.object(parse_ib_xml_file, "IB_AWS_TIMEOUT_MILLISECONDS", 6000000):
                with self.s3_setup(s3_client):
                    ib_upload_obj = IBUpload(event=test_input_event["input"])
                    result = ib_upload_obj.file_to_json(test_lambda_context)

        assert result["bbg_files"]["IB_XML_to_process"] is False

    def test_process_part_file_processed(self, s3_client, test_lambda_context):
        test_input_event = setup_msg_ib_step_message(client_name=CLIENT_NAME)
        test_lambda_context.time_limit_in_seconds = 900

        with patch.object(process_single_conversation, "IB_UPLOAD_TO_ES", False):
            with patch.object(parse_ib_xml_file, "IB_AWS_TIMEOUT_MILLISECONDS", 6000000):
                with self.s3_setup(s3_client):
                    ib_upload_obj = IBUpload(event=test_input_event["input"])
                    result = ib_upload_obj.file_to_json(test_lambda_context)

        assert result["bbg_files"]["IB_XML_to_process"] is True
        assert result["bbg_files"]["IB_XML_record_number"] == 1

    def test_process_intermediate_part_file_processed(self, s3_client, test_lambda_context):
        test_input_event = setup_msg_ib_step_message(client_name=CLIENT_NAME, IB_XML_No=2)
        test_lambda_context.time_limit_in_seconds = 900

        with patch.object(process_single_conversation, "IB_UPLOAD_TO_ES", False):
            with patch.object(parse_ib_xml_file, "IB_AWS_TIMEOUT_MILLISECONDS", 6000000):
                with self.s3_setup(s3_client):
                    ib_upload_obj = IBUpload(event=test_input_event["input"])
                    result = ib_upload_obj.file_to_json(test_lambda_context)

        assert result["bbg_files"]["IB_XML_to_process"] is True
        assert result["bbg_files"]["IB_XML_record_number"] == 2


class TestDebugFunctions:
    @contextmanager
    def s3_setup(self, s3_client):
        bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": "eu-west-1"})

        IB_file_key = "dev.todo.bbg/2020-03-16/decoded/f848135.ib.200316.xml"
        IB_file_location = f"{BASE_DIR}/fixtures/new_bbg/f908067.ib19.210302.xml"
        with open(IB_file_location, "rb") as f:
            s3_client.upload_fileobj(f, BUCKET_NAME, IB_file_key)

        IB_tar_key = "dev.todo.bbg/2020-03-16/decoded/f848135.att.200316.tar.gz"
        IB_tar_location = f"{BASE_DIR}/fixtures/new_bbg/f908067.ib19.att.210302.tar.gz"
        with open(IB_tar_location, "rb") as f:
            s3_client.upload_fileobj(f, BUCKET_NAME, IB_tar_key)

        yield

    def test_process_full_file_processed(self, s3_client, test_lambda_context):
        test_input_event = setup_msg_ib_step_message(client_name=CLIENT_NAME)
        test_lambda_context.time_limit_in_seconds = 90000

        with patch.object(process_single_conversation, "IB_UPLOAD_TO_ES", False):
            with self.s3_setup(s3_client):
                ib_upload_obj = IBUpload(event=test_input_event["input"])
                result = ib_upload_obj.file_to_json(test_lambda_context)

        assert result["bbg_files"]["IB_XML_to_process"] is False
