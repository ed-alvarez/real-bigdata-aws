import os
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path

import boto3
import pytest
from dotenv import dotenv_values
from moto import mock_s3, mock_ssm

BASE_DIR = Path(__file__).resolve().parent

CLIENT_NAME = "testing"
BUCKET_NAME = f"dev-{CLIENT_NAME}.ips"
S3_FIXTURES_DIR = f"{BASE_DIR}/shared_tests/fixtures"


@pytest.fixture(autouse=True)
def add_default_region_aws():
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"


@contextmanager
def parameters_zoom_setup(secrets_client):
    zoom_env_path = f"{BASE_DIR}/zoom_ingest/.env"

    config = {
        **dotenv_values(zoom_env_path),  # load shared development variables
        **os.environ,  # override loaded values with environment variables
    }

    secrets_client.put_parameter(
        Name=f"/{config['TEST']}/zoom_AccountID",
        Description=f"{config['TEST']} zoom AccountID",
        Value=config["zoom_AccountID"],
        Type="String",
    )

    secrets_client.put_parameter(
        Name=f"/{config['TEST']}/zoom_ClientID",
        Description=f"{config['TEST']} zoom ClientID",
        Value=config["zoom_ClientID"],
        Type="String",
    )

    secrets_client.put_parameter(
        Name=f"/{config['TEST']}/zoom_ClientSecret",
        Description=f"{config['TEST']} zoom ClientSecret",
        Value=config["zoom_ClientSecret"],
        Type="SecureString",
    )

    secrets_client.put_parameter(
        Name=f"/{config['TEST']}/zoom_url_api_oauth",
        Description=f"{config['TEST']} zoom _url_api_oauth",
        Value=config["zoom_url_api_oauth"],
        Type="SecureString",
    )

    secrets_client.put_parameter(
        Name=f"/{config['TEST']}/zoom_url_api_token",
        Description=f"{config['TEST']} zoom _url_api_token",
        Value=config["zoom_url_api_token"],
        Type="SecureString",
    )

    secrets_client.put_parameter(
        Name=f"/{config['TEST']}/zoom_url_api_authorize",
        Description=f"{config['TEST']} zoom _url_api_authorize",
        Value=config["zoom_url_api_authorize"],
        Type="SecureString",
    )
    yield


@pytest.fixture
def ssm_zoom_setup(ssm_client):
    result = parameters_zoom_setup(secrets_client=ssm_client)
    yield result


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
        conn = boto3.client("s3", region_name=AWS_REGION)
        yield conn


@pytest.fixture
def ssm_client(aws_credentials):
    with mock_ssm():
        conn = boto3.client("ssm", region_name=AWS_REGION)
        yield conn
