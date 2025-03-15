import sys
from datetime import datetime
from pathlib import Path

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_settings import fileStore, processingStage
from teams_src.teams_shared_modules import paths_helper_functions

test_time_1: datetime = datetime(2017, 11, 28, 23, 55, 59, 342380)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class TestFunctions:
    def test_generate_date_directory(self):
        response: str = paths_helper_functions._generate_date_directory(date=test_time_1)
        assert response == "2017-11-28"

    def test_generate_file_path_s3(self):
        paths_helper_functions.FILE_STORE = fileStore.S3.value
        paths_helper_functions.STAGE = "prod"
        response: str = paths_helper_functions.generate_processing_stage_file_path(
            name="test_file", date=test_time_1, teams_processing_stage=processingStage.todo
        )
        assert response == "todo.teams/2017-11-28/test_file.json"

    def test_generate_file_path_local(self):
        paths_helper_functions.FILE_STORE = fileStore.Local.value
        paths_helper_functions.STAGE = "dev"
        response: str = paths_helper_functions.generate_processing_stage_file_path(
            name="test_file", date=test_time_1, teams_processing_stage=processingStage.todo
        )
        assert response == f"{BASE_DIR}/dev.todo.teams/2017-11-28/test_file.json"

    def test_generate_file_path_s3_attachment(self):
        paths_helper_functions.FILE_STORE = fileStore.S3.value
        paths_helper_functions.STAGE = "dev"
        file_archive_name = "7cc93d51-e5a2-492e-af3b-614a3da8f921"
        file_extension = ".zip"
        response = paths_helper_functions.generate_processing_stage_file_path(
            name=file_archive_name,
            date=test_time_1,
            teams_processing_stage=processingStage.processed,
            file_ext=file_extension,
        )

        assert response == "dev.processed.teams/2017-11-28/7cc93d51-e5a2-492e-af3b-614a3da8f921.zip"
