from collections import OrderedDict
from pathlib import Path

import pytest
from voice_settings import cdrType
from voice_src.process_transcript_job.elastic_search.es_voice_index_v1 import VOICE
from voice_src.process_transcript_job.process_transcript import ProcessTranscript

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def deep_get(d, keys):
    if not keys or d is None:
        return d
    return deep_get(d.get(keys[0]), keys[1:])


class TestFunctions:
    event = {"detail": {"TranscriptionJobName": "fred"}}

    def test__parse_cdr(self, test_lambda_context):
        cdr_dict = {"callerPhoneNumber": "123", "dialedPhoneNumber": "345", "callStartTime": "1634749641"}
        cdr_type = cdrType.redbox

        test_obj = ProcessTranscript(event=self.event, context=test_lambda_context)
        result = test_obj._parse_cdr(cdr_dict=cdr_dict, cdr_type=cdr_type)
        assert type(result) == VOICE

    valid_event = {"detail": {"TranscriptionJobName": "fred", "TranscriptionJobStatus": "COMPLETED"}}
    invalid_event = {
        "detail": {
            "TranscriptionJobName": "valeur-1634897863.42992-1634941532-009279",
            "TranscriptionJobStatus": "FAILED",
            "FailureReason": "The input media file length is too small. Minimum audio duration is 0.500000 milliseconds. Check the length of the file and try your request again.",
        }
    }

    test_1 = (valid_event, True)
    test_2 = (invalid_event, False)

    CASES = [test_1, test_2]

    @pytest.mark.parametrize("event, expected", CASES)
    def test__is_valid_transcript(self, event, expected, test_lambda_context):
        test_obj = ProcessTranscript(event=self.event, context=test_lambda_context)
        result = test_obj._is_valid_transcript(event=event)
        assert result == expected

    dict_1 = OrderedDict(
        [
            ("callerid", "8912351"),
            ("role", "Caller"),
            ("start_time", "2022.01.13 14:02:31.614"),
            ("end_time", "2022.01.13 14:03:15.566"),
            ("end_cause", "0"),
        ]
    )
    dict_2 = OrderedDict(
        [
            ("callerid", "009711056757#"),
            ("role", "Called"),
            ("start_time", "2022.01.13 14:02:31.614"),
            ("end_time", "2022.01.13 14:03:15.575"),
            ("end_cause", "0"),
        ]
    )
    list_1 = [dict_1, dict_2]

    case1 = (
        "/voice_tests/test_data/verba/8912351--009711056757#_2022-01-13_14-02.xml",
        ".xml",
        ["participants", "participant"],
        list_1,
    )
    case2 = ("/voice_tests/test_data/redbox/00002471-0000-0001-2018-020507414049.json", ".json", ["dialedPhoneNumber"], "02070002034")
    case3 = (
        "/voice_tests/test_data/thetalake_ringcentral/2020-06-25.meta.f0f5cba1-a457-4f44-edb8-12def04cd9e0.json",
        ".json",
        ["Participants", "callee"],
        [{"Extension": "62350"}],
    )

    CASES = [case1, case2, case3]

    @pytest.mark.parametrize("file, extension, key, expected", CASES)
    def test__decode_file_content_to_dict_xml(self, file, extension, key, expected, test_lambda_context):
        with open(f"{BASE_DIR}{file}") as cdr:
            content = cdr.read()
        test_obj = ProcessTranscript(event=self.event, context=test_lambda_context)
        result = test_obj._decode_file_content_to_dict(extension=extension, content=content)
        assert deep_get(result, key) == expected

    test_1 = ("fred.xml", ".xml")
    test_2 = ("root/dir/fred.json", ".json")
    test_3 = ("root.top.level/dir.another.level/fred.xls", ".xls")
    test_4 = ("encrypted.xls.gpg", ".gpg")
    CASES = [test_1, test_2, test_3, test_4]

    @pytest.mark.parametrize("key, expected", CASES)
    def test__file_extension_of_cdr(self, key, expected, test_lambda_context):
        test_obj = ProcessTranscript(event=self.event, context=test_lambda_context)
        test_key = {"Key": key, "Bucket": "bucket.ips"}
        result = test_obj._file_extension_of_cdr(key=test_key)
        assert result == expected
