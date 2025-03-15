import os
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path

import boto3
import pytest
from moto import mock_dynamodb, mock_s3, mock_ssm, mock_stepfunctions

BASE_DIR = Path(__file__).resolve().parent

AWS_REGION = os.environ.get("AWS_Region", "eu-west-1")


@pytest.fixture(scope="session")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def s3_client(aws_credentials):
    with mock_s3():
        yield boto3.client("s3", region_name=AWS_REGION)


@pytest.fixture
def step_fn_client(aws_credentials):
    with mock_stepfunctions():
        yield boto3.client("stepfunctions")


@pytest.fixture
def ssm_client(aws_credentials):
    with mock_ssm():
        yield boto3.client("ssm", region_name=AWS_REGION)


@pytest.fixture
def ddb_client(aws_credentials):
    with mock_dynamodb():
        conn = boto3.client("dynamodb", region_name=AWS_REGION)
        yield conn


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


@pytest.fixture
def test_lambda_context(time_limit_in_seconds=120):
    context_obj = TestLambdaContext(time_limit_in_seconds=time_limit_in_seconds)
    yield context_obj


class fakeSftpClient:
    def __init__(self, manifest, sftp_files, sftp_file_local=None):
        self.manifest = manifest
        self.sftp_files = sftp_files
        self.sftp_file_local = sftp_file_local

    def list_files_in_directory(self, *args, **kwargs):
        return self.sftp_files

    def get_files_in_directory(self):
        return self.sftp_files

    def get_file_line_items(self, not_used_param):
        return self.manifest

    def list_of_files_containing(self, containing, remote_dir="."):
        return self.sftp_files

    def download_files_to_tmp(self, files_to_retrieve):
        return [f"tmp/{x}" for x in self.sftp_files]

    def get_sftp_file(self, file_name):
        with open(self.sftp_file_local, "rb") as input:
            return input.read()


@pytest.fixture
def fake_sftp_client(request):
    yield fakeSftpClient(**request.param)
