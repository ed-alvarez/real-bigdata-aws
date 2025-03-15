import os
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_src.teams_data_processing_and_ingest.teams_conversation import (
    zip_and_file_helper_functions,
)

AWS_REGION = os.environ.get("AWS_Region", "eu-west-1")
BASE_DIR = Path(__file__).resolve().parent.parent.parent

CLIENT_NAME = "testing"
BUCKET_NAME = f"{CLIENT_NAME}.ips"


class TestFunctions:
    @contextmanager
    def s3_setup(self, s3_client):
        bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": AWS_REGION})
        yield

    def test_add_file_to_zip(self):
        file_name = f"{BASE_DIR}/data/attachment_bytefile"
        file = open(file_name, "rb")
        bytestring = file.read()
        file_name = "Screenshot 2021-01-27 at 12.23.40.png"
        response = zip_and_file_helper_functions.add_file_to_zip_archive(file_name=file_name, file_content=bytestring)
        assert response

    def test_save_attachments_archive_to_disk(self, s3_client):
        file = open(f"{BASE_DIR}/data/attachment_bytefile", "rb")
        bytestring = file.read()
        file_name = "Screenshot 2021-01-27 at 12.23.40.png"
        file_archive_name = "7cc93d51-e5a2-492e-af3b-614a3da8f921"
        date_time = datetime(2020, 5, 17, 00, 00, 00)
        zip_archive = zip_and_file_helper_functions.add_file_to_zip_archive(file_name=file_name, file_content=bytestring)
        with self.s3_setup(s3_client):
            response = zip_and_file_helper_functions.save_item_archive_to_disk(
                client=CLIENT_NAME,
                date_time=date_time,
                attachment_data=zip_archive,
                file_archive_name=file_archive_name,
            )
        assert response == "dev.processed.teams/2020-05-17/7cc93d51-e5a2-492e-af3b-614a3da8f921.zip"
        s3_objects = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix="dev.processed.teams",
        )
        assert "dev.processed.teams/2020-05-17/7cc93d51-e5a2-492e-af3b-614a3da8f921.zip" in s3_objects["Contents"][0]["Key"]
