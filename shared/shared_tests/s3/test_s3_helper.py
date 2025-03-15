import datetime
from pathlib import Path

import pytest
from freezegun import freeze_time

from shared.shared_src.s3.s3_helper import S3Helper

CLIENT_NAME = "testing"
INGEST_TYPE = "voice"
FAKE_TIME = datetime.datetime(year=2020, month=12, day=25, hour=17, minute=5, second=55, microsecond=3030)
BASE_DIR = Path(__file__).resolve().parent.parent


class TestS3Funcs:
    def test_list_files_with_prefix_return_file(self, shared_s3_setup):
        with shared_s3_setup:
            test_obj: S3Helper = S3Helper(client_name=CLIENT_NAME, ingest_type=INGEST_TYPE)
            result = test_obj.list_files_with_prefix(prefix="")
            assert len(result) == 2
            assert "todo.voice/2021-09-22/20210922-151637_1632316597.19842.json.gpg" in result

    def test_list_files_with_prefix_no_return_file(self, shared_s3_setup):
        with shared_s3_setup:
            test_obj: S3Helper = S3Helper(client_name=CLIENT_NAME, ingest_type=INGEST_TYPE)
            result = test_obj.list_files_with_prefix(prefix="fred")
            assert result == []

    def test_write_file_to_s3(self, shared_s3_setup):
        with open(f"{BASE_DIR}/fixtures/gpg/default_key.pem", "rb") as f:
            file_content = f.read()
        key = "todo.voice/default_key.pem"
        with shared_s3_setup:
            test_obj: S3Helper = S3Helper(client_name=CLIENT_NAME, ingest_type=INGEST_TYPE)
            result = test_obj.write_file_to_s3(file_key=key, file_content=file_content)
            assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
