import os
from contextlib import contextmanager
from typing import List

import pytest
from bbg_helpers.helper_dataclass import BbgFiles
from bbg_src.file_archive_lambda import file_archive

# run in stage mode with: DEV_MODE=0 pytest bbg_tests
if os.environ.get("DEV_MODE", "1") == "1":
    TODO_FOLDER = "dev.todo.bbg"
    PROCESSED_FOLDER = "dev.processed.bbg"
    ARCHIVE_FOLDER = "dev.archive.bbg"
else:
    TODO_FOLDER = "todo.bbg"
    PROCESSED_FOLDER = "processed.bbg"
    ARCHIVE_FOLDER = "archive.bbg"
    os.environ["STAGE"] = "stage"
    os.environ["AWS_EXECUTION_ENV"] = "1"

CLIENT_NAME = "testing"
FIXTURES_DIR = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir)) + "/fixtures/"

INPUT = {
    "client_name": CLIENT_NAME,
    "files_downloaded": [],
    "files_decoded": [
        f"{TODO_FOLDER}/2020-03-16/decoded/f848135.att.200316.tar.gz",
        f"{TODO_FOLDER}/2020-03-16/decoded/f848135.att.200316.tar.gz.sig",
        f"{TODO_FOLDER}/2020-03-16/decoded/f848135.dscl.200316.xml",
        f"{TODO_FOLDER}/2020-03-16/decoded/f848135.dscl.200316.xml.sig",
        f"{TODO_FOLDER}/2020-03-16/decoded/f848135.ib.200316.xml",
        f"{TODO_FOLDER}/2020-03-16/decoded/f848135.ib.200316.xml.sig",
        f"{TODO_FOLDER}/2020-03-16/decoded/f848135.msg.200316.xml",
        f"{TODO_FOLDER}/2020-03-16/decoded/f848135.msg.200316.xml.sig",
    ],
    "has_files": False,
    "error": False,
    "error_msg": "",
    "bbg_client_id": "mc843476559",
    "bbg_manifest": "DAILY",
    "manifest_date": "210205",
    "wait_until": "",
    "bbg_files": {
        "MSG_XML_to_process": False,
        "MSG_file_name": f"{TODO_FOLDER}/2020-03-16/decoded/f848135.msg.200316.xml",
        "MSG_ATT_file_name": f"{TODO_FOLDER}/2020-03-16/decoded/f848135.att.200316.tar.gz",
        "MSG_XML_record_number": 0,
        "IB_XML_to_process": False,
        "IB_file_name": f"{TODO_FOLDER}/2020-03-16/decoded/f848135.ib.200316.xml.gpg",
        "IB_ATT_file_name": f"{TODO_FOLDER}/2020-03-16/decoded/f848135.att.200316.tar.gz",
        "IB_XML_record_number": 0,
    },
}
BUCKET_NAME = f"{CLIENT_NAME}.ips"

DOWNLOADED_FILES = [
    "/2020-03-16/downloaded/daily_manifest_current.txt",
    "/2020-03-16/downloaded/f848135.att.200316.tar.gz.gpg",
    "/2020-03-16/downloaded/f848135.att.200316.tar.gz.sig",
    "/2020-03-16/downloaded/f848135.dscl.200316.xml.gpg",
    "/2020-03-16/downloaded/f848135.dscl.200316.xml.sig",
    "/2020-03-16/downloaded/f848135.ib.200316.xml.gpg",
    "/2020-03-16/downloaded/f848135.ib.200316.xml.sig",
    "/2020-03-16/downloaded/f848135.msg.200316.xml.gpg",
    "/2020-03-16/downloaded/f848135.msg.200316.xml.sig",
]

DECODED_FILES = [
    "/2020-03-16/decoded/f848135.att.200316.tar.gz",
    "/2020-03-16/decoded/f848135.dscl.200316.xml",
    "/2020-03-16/decoded/f848135.ib.200316.xml",
    "/2020-03-16/decoded/f848135.msg.200316.xml",
]


def _construct_file_list(prepend: str, file_list: List) -> List:
    new_file_list: List = []
    file: str
    for file in file_list:
        new_file_list.append(f"{prepend}{file}")
    return new_file_list


class TestHelperFN:
    def test_generate_example_file(self):
        bbg_params: BbgFiles = BbgFiles(**INPUT["bbg_files"])
        result = file_archive.generate_example_file(bbg_params=bbg_params)
        assert result == f"{TODO_FOLDER}/2020-03-16/decoded/f848135.ib.200316.xml.gpg"

    def test_generate_date_prefix(self):
        example_file = "dev.todo.bbg/2020-03-16/decoded/f848135.ib.200316.xml.gpg"
        result = file_archive.generate_directory_prefix(file_name=example_file)
        assert result == "dev.todo.bbg/2020-03-16/"


class TestFileArchive:
    todo_files: List = _construct_file_list(TODO_FOLDER, DOWNLOADED_FILES + DECODED_FILES)
    processed_files: List = _construct_file_list(PROCESSED_FOLDER, DOWNLOADED_FILES + DECODED_FILES)
    archive_files: List = _construct_file_list(ARCHIVE_FOLDER, DOWNLOADED_FILES + DECODED_FILES)

    def s3_setup(self, s3_client):
        # create mock s3 bucket and upload source files
        bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": "eu-west-1"})

        return bucket

    @contextmanager
    def s3_context(self, s3_client):
        yield

    def test_file_archive(self, s3_client, test_lambda_context):

        s3_bucket = self.s3_setup(s3_client)

        for s3path in self.todo_files:
            filename = FIXTURES_DIR + s3path.split("/", 1)[-1]
            s3_client.upload_file(filename, BUCKET_NAME, f"{s3path}")

        # check input files are present in bucket
        bucket_obj = s3_client.list_objects_v2(Bucket=BUCKET_NAME)["Contents"]
        bucket_keys = [file["Key"] for file in bucket_obj]
        expected_keys = self.todo_files
        bucket_keys.sort()
        expected_keys.sort()
        assert bucket_keys == expected_keys

        with self.s3_context(s3_client):
            file_archive.lambda_handler(INPUT, test_lambda_context)

        new_bucket_obj = s3_client.list_objects_v2(Bucket=BUCKET_NAME)["Contents"]
        new_bucket_keys = [file["Key"] for file in new_bucket_obj]
        new_expected_keys = self.processed_files + self.archive_files
        new_bucket_keys.sort()
        new_expected_keys.sort()
        # print('bucket_keys', bucket_keys)
        # print('expected_keys', expected_keys)
        assert bucket_keys == expected_keys
