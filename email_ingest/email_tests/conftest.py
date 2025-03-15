from contextlib import contextmanager
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent

CLIENT_NAME = "test-ips"
BUCKET_NAME = f"{CLIENT_NAME}.ips"
S3_FIXTURES_DIR = f"{BASE_DIR}/sample_emails"


@contextmanager
def s3_email_setup(s3_client):
    bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": "eu-west-1"})
    s3_mock_upload_list = []

    file_1 = (f"todo.email/mime/4ho0o54uiim77vmpsmkl8jbchtn2utci5ai382g1", f"{S3_FIXTURES_DIR}/naya_group")
    s3_mock_upload_list.append(file_1)

    file_2 = (
        f"todo.email/mime/6acuef8chlnhis6hm68dth57gli2a98ngckrj1o1",
        f"{S3_FIXTURES_DIR}/ayora_disposition",
    )
    s3_mock_upload_list.append(file_2)

    for file_pair in s3_mock_upload_list:
        mock_s3_upload(local_filename=file_pair[1], s3_key=file_pair[0], s3_client=s3_client)

    yield


def mock_s3_upload(local_filename, s3_key, s3_client):
    with open(local_filename, "rb") as f:
        s3_client.upload_fileobj(f, BUCKET_NAME, s3_key)


@pytest.fixture
def email_s3_setup(s3_client):
    result = s3_email_setup(s3_client)
    yield result
