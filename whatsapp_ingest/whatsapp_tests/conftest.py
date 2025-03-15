import os
from datetime import datetime, timedelta

import boto3
import pytest
from moto import mock_s3, mock_ssm


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def s3_client(aws_credentials):
    with mock_s3():
        conn = boto3.client("s3", region_name="eu-west-1")
        yield conn


@pytest.fixture
def ssm_client(aws_credentials):
    with mock_ssm():
        conn = boto3.client("ssm", region_name="eu-west-1")
        yield conn


class TestLambdaContext:
    def __init__(self, time_limit_in_seconds=120):
        self.log_group_name = "local_test_log_group_name"
        self.log_stream_name = "local_test_log_stream_name"
        self.aws_request_id = "local_test_aws_request_id"
        self.start_time = datetime.now()
        self.time_limit_in_seconds = time_limit_in_seconds

    def get_remaining_time_in_millis(self):
        self.end_time = self.start_time + timedelta(seconds=self.time_limit_in_seconds)
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
