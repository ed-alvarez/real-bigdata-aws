from pathlib import Path
from typing import List

import pytest

from shared.shared_src.tar_file_utils import (
    extract_file_from_tar,
    match_file_name,
    xstr,
)


class TestXstring:
    CASES = [(None, ""), ("Fred", "Fred")]

    @pytest.mark.parametrize("input, expected", CASES)
    def test_none_case(self, input, expected):
        result = xstr(s=input)
        assert result == expected


class TestTarFile:
    BASE_DIR = Path(__file__).resolve().parent.parent
    original_archive = f"{BASE_DIR}/shared_tests/fixtures/archive_files/f848135.att.210521.tar.gz"
    new_ib_archive = f"{BASE_DIR}/shared_tests/fixtures/archive_files/f848135.ib19.att.210521.tar.gz"
    new_msg_archive = f"{BASE_DIR}/shared_tests/fixtures/archive_files/f848135.msg.att.210521.tar.gz"

    CASES = [
        (original_archive, "60A7BC8C0000EB9307F52E21.pdf", 106408),
        (new_ib_archive, "10769949_european%20financials%20daily_60A75A1801440128064D0001.pdf", 276492),
        (new_msg_archive, "60A806730000D85907FC1D65.xlsx", 1162652),
    ]

    @pytest.mark.parametrize("tarFileName, fileName, expected", CASES)
    def test_file_retrieval_original_bbg_archive(self, tarFileName, fileName, expected):
        tarFileContents = open(tarFileName, "rb").read()
        result = extract_file_from_tar(fileName, tarFileName, tarFileContents)
        assert len(result) == expected


class TestMatchFileName:
    filelist: List = ["file1", "file2", "file3", "directory\\file4"]
    test_find_file: str = "file2"
    test_find_file_diff_case = "FILE3"
    test_find_partial_match = "file4"
    test_dont_find_a_file = "file6"

    CASES = [
        (filelist, test_find_file, "file2"),
        (filelist, test_find_file_diff_case, "file3"),
        (filelist, test_find_partial_match, "directory\\file4"),
        (filelist, test_dont_find_a_file, ""),
        ([], test_find_file, ""),
    ]

    @pytest.mark.parametrize("fileList, fileName, expected", CASES)
    def test_find_in_list(self, fileList, fileName, expected):
        result = match_file_name(list_of_files=fileList, original_file_name=fileName)
        assert result == expected
