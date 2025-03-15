from contextlib import contextmanager
from pathlib import Path

import pytest
from bbg_src.file_download_lambda.file_download import BBGFileDownload

BASE_DIR = Path(__file__).resolve().parent.parent

CLIENT_NAME = "testing"
BUCKET_NAME = f"{CLIENT_NAME}.ips"


@pytest.fixture()
def daily_event_no_date():
    return {"bbg_client_id": "mc913915589", "client_name": f"{CLIENT_NAME}", "bbg_manifest": "DAILY"}


@pytest.fixture()
def daily_event_date():
    return {
        "bbg_client_id": "mc913915589",
        "client_name": f"{CLIENT_NAME}",
        "bbg_manifest": "DAILY",
        "manifest_date": "200827",
    }


@pytest.fixture()
def archive_event():
    return {
        "bbg_client_id": "mc913915589",
        "client_name": f"{CLIENT_NAME}",
        "bbg_manifest": "ARCHIVE",
        "manifest_date": "200818",
    }


@pytest.fixture()
def wait_event_input_missing_mainfest():
    return {
        "client_name": f"{CLIENT_NAME}",
        "files_downloaded": [],
        "files_decoded": [],
        "has_files": False,
        "error": True,
        "error_msg": "Not all files required by decode are available.  Missing msg",
        "bbg_client_id": "mc1126917282",
        "bbg_manifest": "DAILY",
        "manifest_date": "210608",
        "wait_until": "2021-06-10T17:00:00Z",
    }


@pytest.fixture()
def wait_event_input_missing_sftp():
    return {
        "client_name": f"{CLIENT_NAME}",
        "files_downloaded": [],
        "files_decoded": [],
        "has_files": False,
        "error": True,
        "error_msg": "Manifest files missing from sFTP: f848135.msg.190329.xml.gpg,f848135.msg.190329.xml.sig",
        "bbg_client_id": "mc1126917282",
        "bbg_manifest": "DAILY",
        "manifest_date": "210608",
        "wait_until": "2021-06-10T17:00:00Z",
    }


class TestGenerateManifestFileNameClass:
    def test_remove_file_from_file_list(self, daily_event_date):
        file_download = BBGFileDownload(event=daily_event_date)

        files_in_directory = [
            "daily_manifest_wget_current.html",
            "daily_manifest_current.txt",
            "daily_manifest_wget_200827.html",
            "daily_manifest_200827.txt",
            "daily_manifest_200826.txt.gz",
            "daily_manifest_wget_200831.html",
            "daily_manifest_wget_200826.html.gz",
            "daily_manifest_200831.txt",
            "daily_manifest_wget_200828.html",
            "daily_manifest_200828.txt",
        ]

        expected_result = [
            "daily_manifest_current.txt",
            "daily_manifest_200827.txt",
            "daily_manifest_200826.txt.gz",
            "daily_manifest_200831.txt",
            "daily_manifest_200828.txt",
        ]

        list_of_manifest_files = file_download.remove_file_from_file_lists(files_in_directory, parts_to_remove=[".html", ".html.gz"])
        assert len(list_of_manifest_files) == 5
        assert list_of_manifest_files == expected_result

    def test_get_full_file_from_partial_match(self, daily_event_date):
        file_download = BBGFileDownload(event=daily_event_date)
        list_of_files = [
            "daily_manifest_current.txt",
            "daily_manifest_200827.txt",
            "daily_manifest_200826.txt.gz",
            "daily_manifest_200831.txt",
            "daily_manifest_200828.txt",
        ]

        file_name = "daily_manifest_200826.txt"

        manifest_full_file_name = file_download.get_full_file_from_partial_match(
            file_partial_match=file_name, list_of_files=list_of_files
        )
        assert manifest_full_file_name == "daily_manifest_200826.txt.gz"

    def test_generate_manifest_name_daily_no_date(self, daily_event_no_date):
        file_download = BBGFileDownload(event=daily_event_no_date)
        # NB do NOT need to instatiate sFTP to check/translate file name
        manifest_name = file_download.generate_manifest_file_name()
        assert manifest_name == "daily_manifest_current.txt"


class TestGenerateManifestFileContentsClass:
    parameters = {
        "manifest": "daily_manifest_current.txt",
        "sftp_files": [
            "daily_manifest_wget_current.html",
            "daily_manifest_current.txt",
            "daily_manifest_wget_200827.html",
            "daily_manifest_200827.txt",
            "daily_manifest_200826.txt.gz",
            "daily_manifest_wget_200831.html",
            "daily_manifest_wget_200826.html.gz",
            "daily_manifest_200831.txt",
            "daily_manifest_wget_200828.html",
            "daily_manifest_200828.txt",
        ],
    }

    @pytest.mark.parametrize(
        "fake_sftp_client",
        [parameters],
        indirect=[
            "fake_sftp_client",
        ],
    )
    def test_generate_manifest_name_daily_date(self, daily_event_date, fake_sftp_client):
        file_download = BBGFileDownload(event=daily_event_date)
        file_download._sftp_client = fake_sftp_client
        manifest_name = file_download.generate_manifest_file_name()
        assert manifest_name == "daily_manifest_200827.txt"


class TestCheckAllFilesArePresentClass:
    def test_check_all_ips_required_files_are_on_sftp_site_success(self, daily_event_no_date):
        file_download = BBGFileDownload(event=daily_event_no_date)
        files_to_retrieve = [
            "f848135.msg.190329.xml.gpg",
            "f848135.dscl.190329.xml.gpg",
            "f848135.ib.190329.xml.gpg",
            "f848135.msg.190329.xml.sig",
            "f848135.dscl.190329.xml.sig",
            "f848135.ib.190329.xml.sig",
            "f848135.att.190329.tar.gz.gpg",
            "f848135.att.190329.tar.gz.sig",
        ]

        ips_required_files = file_download.check_all_ips_required_files_are_on_sftp_site(files_to_retrieve)
        assert ips_required_files == {"ib19", "msg.att", "ib19.att"}

    def test_check_all_ips_required_files_are_on_sftp_site_fail(self, daily_event_no_date):
        file_download = BBGFileDownload(event=daily_event_no_date)

        # Missing MSG Files
        files_to_retrieve = [
            "f848135.dscl.190329.xml.gpg",
            "f848135.ib.190329.xml.gpg",
            "f848135.dscl.190329.xml.sig",
            "f848135.ib.190329.xml.sig",
            "f848135.att.190329.tar.gz.gpg",
            "f848135.att.190329.tar.gz.sig",
        ]

        ips_required_files = file_download.check_all_ips_required_files_are_on_sftp_site(files_to_retrieve)
        assert ips_required_files == {"ib19", "msg.att", "ib19.att", "msg"}

    def test_november_check_all_ips_required_files_are_on_sftp_site_fail(self, daily_event_no_date):
        file_download = BBGFileDownload(event=daily_event_no_date)
        # Missing MSG Files

        files_to_retrieve = [
            "f961819.msg.211101.xml.gpg",
            "f961819.dscl.211101.xml.gpg",
            "f961819.ib19.211101.xml.gpg",
            "f961819.msg.211101.xml.sig",
            "f961819.dscl.211101.xml.sig",
            "f961819.ib19.211101.xml.sig",
            "f961819.ib19.att.211101.tar.gz.gpg",
            "f961819.msg.att.211101.tar.gz.gpg",
            "f961819.ib19.att.211101.tar.gz.sig",
            "f961819.msg.att.211101.tar.gz.sig",
        ]

        ips_required_files = file_download.check_all_ips_required_files_are_on_sftp_site(files_to_retrieve)
        assert ips_required_files == set()

    def test_check_all_manifest_files_are_on_sftp_site_success(self, daily_event_no_date):
        file_download = BBGFileDownload(event=daily_event_no_date)
        files_in_manifest = [
            "f848135.msg.190329.xml.gpg",
            "f848135.dscl.190329.xml.gpg",
            "f848135.ib.190329.xml.gpg",
            "f848135.msg.190329.xml.sig",
            "f848135.dscl.190329.xml.sig",
            "f848135.ib.190329.xml.sig",
            "f848135.att.190329.tar.gz.gpg",
            "f848135.att.190329.tar.gz.sig",
        ]

        files_on_sftp = [
            "f848135.msg.190329.xml.gpg",
            "f848135.dscl.190329.xml.gpg",
            "f848135.ib.190329.xml.gpg",
            "f848135.msg.190329.xml.sig",
            "f848135.dscl.190329.xml.sig",
            "f848135.ib.190329.xml.sig",
            "f848135.att.190329.tar.gz.gpg",
            "f848135.att.190329.tar.gz.sig",
        ]

        missing_files = file_download.check_all_manifest_files_are_on_sftp_site(files_in_manifest, files_on_sftp)
        assert missing_files == list()

    def test_check_all_manifest_files_are_on_sftp_site_fail(self, daily_event_no_date):
        file_download = BBGFileDownload(event=daily_event_no_date)
        files_in_manifest = [
            "f848135.msg.190329.xml.gpg",
            "f848135.dscl.190329.xml.gpg",
            "f848135.ib.190329.xml.gpg",
            "f848135.msg.190329.xml.sig",
            "f848135.dscl.190329.xml.sig",
            "f848135.ib.190329.xml.sig",
            "f848135.att.190329.tar.gz.gpg",
            "f848135.att.190329.tar.gz.sig",
        ]

        files_on_sftp = [
            "f848135.msg.190329.xml.gpg",
            "f848135.dscl.190329.xml.gpg",
            "f848135.ib.190329.xml.gpg",
            "f848135.msg.190329.xml.sig",
            "f848135.dscl.190329.xml.sig",
            "f848135.ib.190329.xml.sig",
            "f848135.att.190329.tar.gz.gpg",
        ]

        missing_files = file_download.check_all_manifest_files_are_on_sftp_site(files_in_manifest, files_on_sftp)
        assert missing_files == ["f848135.att.190329.tar.gz.sig"]

    def test_remove_path_from_file_list(self, daily_event_no_date):
        file_download = BBGFileDownload(event=daily_event_no_date)
        files_with_directory_list = [
            "tmp/f848135.msg.190329.xml.gpg",
            "tmp/f848135.dscl.190329.xml.gpg",
            "tmp/f848135.ib.190329.xml.gpg",
            "tmp/f848135.msg.190329.xml.sig",
            "tmp/f848135.dscl.190329.xml.sig",
            "tmp/f848135.ib.190329.xml.sig",
            "tmp/f848135.att.190329.tar.gz.gpg",
        ]

        files_without_directory_list = [
            "f848135.msg.190329.xml.gpg",
            "f848135.dscl.190329.xml.gpg",
            "f848135.ib.190329.xml.gpg",
            "f848135.msg.190329.xml.sig",
            "f848135.dscl.190329.xml.sig",
            "f848135.ib.190329.xml.sig",
            "f848135.att.190329.tar.gz.gpg",
        ]

        new_file_list = file_download.remove_path_from_file_list(files_with_directory_list)

        assert new_file_list == files_without_directory_list


class TestEndToEnd:
    @contextmanager
    def s3_setup(self, s3_client):
        bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": "eu-west-1"})

        IB_tar_key = "dev.todo.bbg/2020-03-16/downloaded/f848135.att.200316.tar.gz"
        IB_tar_location = f"{BASE_DIR}/fixtures/2020-03-16/downloaded/f848135.att.200316.tar.gz.gpg"
        with open(IB_tar_location, "rb") as f:
            s3_client.upload_fileobj(f, BUCKET_NAME, IB_tar_key)

        yield

    sftp_parameters = {
        "manifest": [
            "f848135.msg.190329.xml.gpg",
            "f848135.dscl.190329.xml.gpg",
            "f848135.ib.190329.xml.gpg",
            "f848135.msg.190329.xml.sig",
            "f848135.dscl.190329.xml.sig",
            "f848135.ib.190329.xml.sig",
            "f848135.att.190329.tar.gz.gpg",
        ],
        "sftp_files": [
            "f848135.dscl.190329.xml.gpg",
            "f848135.ib.190329.xml.gpg",
            "f848135.dscl.190329.xml.sig",
            "f848135.ib.190329.xml.sig",
            "f848135.att.190329.tar.gz.gpg",
        ],
        "sftp_file_local": f"{BASE_DIR}/fixtures/2020-03-16/downloaded/f848135.att.200316.tar.gz.gpg",
    }

    @pytest.mark.parametrize(
        "fake_sftp_client",
        [sftp_parameters],
        indirect=[
            "fake_sftp_client",
        ],
    )
    def test_missing_files_on_sftp_initial(self, s3_client, daily_event_no_date, fake_sftp_client):
        # NB Need to instatiate sFTP to check/translate file name

        with self.s3_setup(s3_client):
            file_download = BBGFileDownload(event=daily_event_no_date)
            file_download._sftp_client = fake_sftp_client
            response = file_download.file_download()

        assert response["error_msg"] == "Manifest files missing from sFTP: f848135.msg.190329.xml.gpg,f848135.msg.190329.xml.sig"

    @pytest.mark.parametrize(
        "fake_sftp_client",
        [sftp_parameters],
        indirect=[
            "fake_sftp_client",
        ],
    )
    def test_missing_files_on_sftp_after_wait(self, s3_client, wait_event_input_missing_sftp, fake_sftp_client):
        # NB Need to instatiate sFTP to check/translate file name

        with self.s3_setup(s3_client):
            file_download = BBGFileDownload(event=wait_event_input_missing_sftp)
            file_download._sftp_client = fake_sftp_client
            response = file_download.file_download()

        assert response["error"] is False
        assert response["error_msg"] == "Manifest files missing from sFTP: f848135.msg.190329.xml.gpg,f848135.msg.190329.xml.sig"

    manifest_parameters = {
        "manifest": [
            "f848135.dscl.190329.xml.gpg",
            "f848135.ib.190329.xml.gpg",
            "f848135.dscl.190329.xml.sig",
            "f848135.ib.190329.xml.sig",
            "f848135.att.190329.tar.gz.gpg",
        ],
        "sftp_files": [
            "f848135.dscl.190329.xml.gpg",
            "f848135.ib.190329.xml.gpg",
            "f848135.dscl.190329.xml.sig",
            "f848135.ib.190329.xml.sig",
            "f848135.att.190329.tar.gz.gpg",
        ],
        "sftp_file_local": f"{BASE_DIR}/fixtures/2020-03-16/downloaded/f848135.att.200316.tar.gz.gpg",
    }

    @pytest.mark.parametrize(
        "fake_sftp_client",
        [manifest_parameters],
        indirect=[
            "fake_sftp_client",
        ],
    )
    def test_missing_files_on_manifest(self, s3_client, daily_event_no_date, fake_sftp_client):
        with self.s3_setup(s3_client):
            file_download = BBGFileDownload(event=daily_event_no_date)
            # Missing MSG files from manifest
            file_download._sftp_client = fake_sftp_client
            response = file_download.file_download()
        assert response["error"] is True

    @pytest.mark.parametrize(
        "fake_sftp_client",
        [manifest_parameters],
        indirect=[
            "fake_sftp_client",
        ],
    )
    def test_missing_files_on_manifest_after_wait(self, s3_client, wait_event_input_missing_mainfest, fake_sftp_client):
        with self.s3_setup(s3_client):
            file_download = BBGFileDownload(event=wait_event_input_missing_mainfest)
            # Missing MSG files from manifest
            file_download._sftp_client = fake_sftp_client
            response = file_download.file_download()
        assert response["error"] is False
        assert response["error_msg"] == "Not all files required by decode are available.  Missing msg"

    parameters = {
        "manifest": [
            "f848135.msg.190329.xml.gpg",
            "f848135.dscl.190329.xml.gpg",
            "f848135.ib.190329.xml.gpg",
            "f848135.msg.190329.xml.sig",
            "f848135.dscl.190329.xml.sig",
            "f848135.ib.190329.xml.sig",
            "f848135.att.190329.tar.gz.gpg",
        ],
        "sftp_files": [
            "f848135.msg.190329.xml.gpg",
            "f848135.dscl.190329.xml.gpg",
            "f848135.ib.190329.xml.gpg",
            "f848135.msg.190329.xml.sig",
            "f848135.dscl.190329.xml.sig",
            "f848135.ib.190329.xml.sig",
            "f848135.att.190329.tar.gz.gpg",
        ],
        "sftp_file_local": f"{BASE_DIR}/fixtures/2020-03-16/downloaded/f848135.att.200316.tar.gz.gpg",
    }

    @pytest.mark.parametrize(
        "fake_sftp_client",
        [parameters],
        indirect=[
            "fake_sftp_client",
        ],
    )
    def test_success_response(self, s3_client, daily_event_no_date, fake_sftp_client):
        with self.s3_setup(s3_client):
            file_download = BBGFileDownload(event=daily_event_no_date)
            file_download._sftp_client = fake_sftp_client
            response = file_download.file_download()

        assert response["error"] is True

    parameters = {
        "manifest": [
            "f848135.msg.190329.xml.gpg.gz",
            "f848135.dscl.190329.xml.gpg.gz",
            "f848135.ib.190329.xml.gpg.gz",
            "f848135.msg.190329.xml.sig.gz",
            "f848135.dscl.190329.xml.sig.gz",
            "f848135.ib.190329.xml.sig.gz",
            "f848135.att.190329.tar.gz.gpg.gz",
        ],
        "sftp_files": [
            "f848135.msg.190329.xml.gpg.gz",
            "f848135.dscl.190329.xml.gpg.gz",
            "f848135.ib.190329.xml.gpg.gz",
            "f848135.msg.190329.xml.sig.gz",
            "f848135.dscl.190329.xml.sig.gz",
            "f848135.ib.190329.xml.sig.gz",
            "f848135.att.190329.tar.gz.gpg.gz",
        ],
        "sftp_file_local": f"{BASE_DIR}/fixtures/2020-03-16/decoded/f848135.att.200316.tar.gz",
    }

    @pytest.mark.parametrize(
        "fake_sftp_client",
        [parameters],
        indirect=[
            "fake_sftp_client",
        ],
    )
    def test_success_response_archived_file(self, s3_client, archive_event, fake_sftp_client):
        with self.s3_setup(s3_client):
            file_download = BBGFileDownload(event=archive_event)
            file_download._sftp_client = fake_sftp_client
            response = file_download.file_download()

        assert response["error"] is False
