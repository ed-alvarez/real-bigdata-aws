from contextlib import contextmanager
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent

CLIENT_NAME = "testing"
BUCKET_NAME = f"{CLIENT_NAME}.ips"
S3_FIXTURES_DIR = f"{BASE_DIR}/fixtures/Decode"


@contextmanager
def parameters_bbg_gpg_setup(ssm_client):
    with open(f"{S3_FIXTURES_DIR}/bbgprivkey.pem") as f:
        priv_key_contents = f.read()

    ssm_client.put_parameter(
        Name=f"/{CLIENT_NAME}/bbg/privkey.pem",
        Description="Client GPG PEM Key",
        Value="dummy_data",
        Type="String",
    )

    ssm_client.put_parameter(
        Name=f"/default/bbgprivkey.pem",
        Description="Default GPG PEM key",
        Value=priv_key_contents,
        Type="String",
    )

    ssm_client.put_parameter(
        Name=f"/{CLIENT_NAME}/bbg/privkeypass",
        Description="Client GPG PEM Key Passcode",
        Value="dummy_data",
        Type="String",
    )
    ssm_client.put_parameter(
        Name=f"/default/bbgprivkeypass",
        Description="default GPG PEM Key Passcode",
        Value="drugs.declaim.calendar",
        Type="String",
    )
    yield


@pytest.fixture
def ssm_bbg_gpg_harness(ssm_client):
    result = parameters_bbg_gpg_setup(ssm_client=ssm_client)
    yield result


@contextmanager
def s3_bbg_gpg_setup(s3_client):
    bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": "eu-west-1"})
    s3_mock_upload_list = []

    file_1 = (f"Architecture High Level.docx.gpg", f"{S3_FIXTURES_DIR}/Architecture High Level.docx.gpg")
    s3_mock_upload_list.append(file_1)

    for file_pair in s3_mock_upload_list:
        mock_s3_upload(local_filename=file_pair[1], s3_key=file_pair[0], s3_client=s3_client)

    yield


def mock_s3_upload(local_filename, s3_key, s3_client):
    with open(local_filename, "rb") as f:
        s3_client.upload_fileobj(f, BUCKET_NAME, s3_key)


@pytest.fixture
def s3_bbg_gpg_harness(s3_client):
    result = s3_bbg_gpg_setup(s3_client)
    yield result
