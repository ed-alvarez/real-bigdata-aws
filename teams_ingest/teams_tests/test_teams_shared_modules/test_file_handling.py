import os
import sys
from contextlib import contextmanager
from pathlib import Path

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_src.teams_shared_modules.file_handling import FileHandling
from teams_tests.data.teams_data_1_day import result1

AWS_REGION = os.environ.get("AWS_Region", "eu-west-1")


BASE_DIR = Path(__file__).resolve().parent.parent.parent
CLIENT_NAME = "testing"
BUCKET_NAME = f"{CLIENT_NAME}.ips"


class TestS3:
    @contextmanager
    def s3_setup(self, s3_client):
        bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": AWS_REGION})
        yield

    def test_save_json(self, s3_client):
        file_name = "teams.todo/2017-11-28/test_file.json"
        with self.s3_setup(s3_client):
            fred: FileHandling = FileHandling.get("s3")(file_name=file_name, client=CLIENT_NAME)
            fred.save_json(data=result1)
            s3_objects = s3_client.list_objects_v2(
                Bucket=BUCKET_NAME,
                Prefix="teams.todo/2017-11-28",
            )
            assert file_name == s3_objects["Contents"][0]["Key"]


class TestLocal:
    def test_save_json(self, s3_client):
        file_name = f"{BASE_DIR}/teams.todo/2017-11-28/test_file.json"
        fred: FileHandling = FileHandling.get("local")(file_name=file_name, client=CLIENT_NAME)
        fred.save_json(data=result1)
        results_path = Path(f"{BASE_DIR}/teams.todo/2017-11-28/")
        results_list = []
        for file in results_path.iterdir():
            results_list.append(file.name)
        assert "test_file.json" in results_list
