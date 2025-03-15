import pytest
from voice_clients_src.valeur.get_files_and_process import IterateDateList

from shared.shared_src.s3.s3_helper import S3Helper


class TestFunctions:

    HTTPStatusCode_fail = {"HTTPStatusCode": 404}
    HTTPStatusCode_OK = {"HTTPStatusCode": 200}
    case1 = {"ResponseMetadata": HTTPStatusCode_fail}
    case2 = {"ResponseMetadata": HTTPStatusCode_OK}
    CASES = [(case1, False), (case2, True)]

    @pytest.mark.parametrize("response, expected", CASES)
    def test__is_copied(self, response, expected):
        test_obj = IterateDateList(date_list=[], client="testing")
        result = test_obj._is_copied(response=response)
        assert result is expected

    CASES = [("20210922-151637_1632316597.19842.json", False), ("20210922-151637_1632316597.19842.wav", True)]

    @pytest.mark.parametrize("file_name, expected", CASES)
    def test__is_audio_file(self, file_name, expected):
        test_obj = IterateDateList(date_list=[], client="testing")
        result = test_obj._is_audio_file(file_name=file_name)
        assert result is expected

    CASES = [
        ("20210922-151637_1632316597.19842.json.gpg", "1632316597.19842.json"),
        ("20210922-151637_1632316597.19842.wav.gpg", "1632316597.19842.wav"),
    ]

    @pytest.mark.parametrize("file_name, expected", CASES)
    def test__generate_s3_file(self, file_name, expected):
        test_obj = IterateDateList(date_list=[], client="testing")
        result = test_obj._generate_s3_file(file_name=file_name)
        assert result == expected

    CASES = [("20210922-151637_1632316597.19842.json.gpg", "2021-09-22"), ("20210922-151637_1632316597.19842.wav.gpg", "2021-09-22")]

    @pytest.mark.parametrize("file_name, expected", CASES)
    def test__generate_s3_date_folder(self, file_name, expected):
        test_obj = IterateDateList(date_list=[], client="testing")
        result = test_obj._generate_s3_date_folder(file_name=file_name)
        assert result == expected

    CASES = [
        ("20210922-151637_1632316597.19842.json.gpg", "todo.voice/2021-09-22/1632316597.19842.json"),
        ("20210922-151637_1632316597.19842.wav.gpg", "todo.voice/2021-09-22/1632316597.19842.wav"),
    ]

    @pytest.mark.parametrize("file_name, expected", CASES)
    def test__generate_s3_file_key(self, file_name, expected):
        test_obj = IterateDateList(date_list=[], client="testing")
        s3_client: S3Helper = S3Helper(client_name="testing", ingest_type="voice")
        result = test_obj._generate_s3_file_key(file_name=file_name, s3_client=s3_client)
        assert result == expected
