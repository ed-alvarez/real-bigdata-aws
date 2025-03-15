"""
Test for api_media.py module
"""
import json
import re
from unittest.mock import patch

import dataclass_wizard
import pytest
from moto import mock_lambda, mock_s3

from shared.shared_src.s3.s3_helper import S3Helper
from shared.shared_src.utils import _webvtt_to_list, webvtt_parse_content
from zoom_ingest.zoom_shared.api_media import MediaController
from zoom_ingest.zoom_shared.zoom_dataclasses import ZoomFilesTracker
from zoom_ingest.zoom_tests.test_zoom_shared.test_zoom_shared_resources import (
    s3_returned_inbound_call_object,
    s3_returned_meet_na_vtt,
    s3_returned_meet_vtt,
    transcript_ok_vtt,
)


@mock_s3
@mock_lambda
class TestApiMedia:

    PATTERN_FOR_VTT = r"\d\n\d\d:\d\d:\d\d.\d\d\d\s-->\s\d\d:\d\d:\d\d.\d\d\d\n(\W*|\w*)*"

    @pytest.fixture
    def empty_zoom_file_tracker(self):
        return {
            "customer": "melqart",
            "period": "custom",
            "if_error": "",
            "start_date": "2022-09-09",
            "end_date": "2022-09-10",
            "bucket_name": "todo",
            "success_step": False,
            "done_workflow": False,
            "calls": [],
            "meets": [],
        }

    def test_empty_arguments_enhance_throw_error(self):
        """
        Test for enhance() when arguments are empty, MediaController __init__ will throw Attribute Error
        """
        with pytest.raises(AttributeError) as error:
            _ = MediaController()
        assert error.typename == "AttributeError"
        assert error.value.args[0] == "'NoneType' object has no attribute 'customer'"

    def test_init_media_controller_with_empty_input(self, empty_zoom_file_tracker):
        """
        Test for MediaController() when only arg zoom_file_tracker is valid object
        """
        zoom_files_tracker = dataclass_wizard.fromdict(ZoomFilesTracker, empty_zoom_file_tracker)
        media_controller = MediaController(zoom_file_tracker=zoom_files_tracker)
        assert media_controller is not None

    def test_enhance_with_empty_uris(self, empty_zoom_file_tracker):
        """
        Test for MediaController() and enhance() when only arg zoom_file_tracker is valid object and no uri to enhance.
        """
        zoom_files_tracker = dataclass_wizard.fromdict(ZoomFilesTracker, empty_zoom_file_tracker)
        media_controller = MediaController(zoom_file_tracker=zoom_files_tracker)
        result = media_controller.enhance()
        assert media_controller is not None
        assert result == zoom_files_tracker

    @patch.object(
        S3Helper,
        "get_file_content",
        return_value=json.dumps(s3_returned_inbound_call_object).encode("utf-8"),
    )
    @pytest.mark.parametrize(
        "call_uri, will_it_be_processed",
        [
            (None, False),
            ("", False),
            ("a6df2784-9ec4-43ce-8845-13275c55da40", True),
        ],
    )
    def test_enhance_blob_call(
        self,
        s3_helper_mocked,
        call_uri,
        will_it_be_processed,
        empty_zoom_file_tracker,
    ):
        """
        Test for enhance_blob_call() when argument has different status
        """
        empty_zoom_file_tracker["calls"] = [call_uri]
        zoom_files_tracker = dataclass_wizard.fromdict(ZoomFilesTracker, empty_zoom_file_tracker)
        media_controller = MediaController(zoom_file_tracker=zoom_files_tracker)
        result = media_controller.enhance(call_uri_to_enhance=call_uri)
        if will_it_be_processed:
            for call in result.calls:
                assert "todo.zoom" in call
        else:
            assert empty_zoom_file_tracker == result.__dict__

    @patch.object(
        S3Helper,
        "get_file_content",
        return_value=json.dumps(s3_returned_meet_na_vtt).encode("utf-8"),
    )
    @pytest.mark.parametrize(
        "meet_uri, will_it_be_processed",
        [
            (None, False),
            ("", False),
            ("6429324446", True),
        ],
    )
    def test_enhance_blob_meet_na_vtt(
        self,
        s3_helper_mocked,
        meet_uri,
        will_it_be_processed,
        empty_zoom_file_tracker,
    ):
        """
        Test for enhance_blob_meet() when argument has different status for none vtt content
        """
        empty_zoom_file_tracker["meets"] = [meet_uri]
        zoom_files_tracker = dataclass_wizard.fromdict(ZoomFilesTracker, empty_zoom_file_tracker)
        media_controller = MediaController(zoom_file_tracker=zoom_files_tracker)
        result = media_controller.enhance(meet_uri_to_enhance=meet_uri)
        if will_it_be_processed:
            for meet in result.meets:
                assert "todo.zoom" in meet
        else:
            assert empty_zoom_file_tracker == result.__dict__

    @patch.object(S3Helper, "get_file_content", return_value=json.dumps(s3_returned_meet_vtt).encode("utf-8"))
    @pytest.mark.parametrize(
        "meet_uri, will_it_be_processed",
        [
            (None, False),
            ("", False),
            ("6429324446", True),
        ],
    )
    def test_enhance_blob_meet_vtt(
        self,
        s3_helper_mocked,
        meet_uri,
        will_it_be_processed,
        empty_zoom_file_tracker,
    ):
        """
        Test for enhance_blob_meet() when argument has different status for vtt content
        """
        empty_zoom_file_tracker["meets"] = [meet_uri]
        zoom_files_tracker = dataclass_wizard.fromdict(ZoomFilesTracker, empty_zoom_file_tracker)
        media_controller = MediaController(zoom_file_tracker=zoom_files_tracker)
        result = media_controller.enhance(meet_uri_to_enhance=meet_uri)
        if will_it_be_processed:
            for meet in result.meets:
                assert "todo.zoom" in meet
        else:
            assert empty_zoom_file_tracker == result.__dict__

    @patch.object(S3Helper, "get_file_content", return_value=None)
    def test_enhance_call_uri_is_not_available_to_download(self, s3_helper_mocked, empty_zoom_file_tracker):
        """
        Attribute error when call binary is not available for downloading due to file does not exist or is not found
        """
        call_uri = "a6df2784-9ec4-43ce-8845-13275c55da40"
        empty_zoom_file_tracker["calls"] = [call_uri]
        zoom_files_tracker = dataclass_wizard.fromdict(ZoomFilesTracker, empty_zoom_file_tracker)
        media_controller = MediaController(zoom_file_tracker=zoom_files_tracker)
        with pytest.raises(AttributeError) as error:
            _ = media_controller.enhance(call_uri_to_enhance=call_uri)
        assert error.typename == "AttributeError"
        assert error.value.args[0] == "'NoneType' object has no attribute 'decode'"

    @patch.object(S3Helper, "get_file_content", return_value=None)
    def test_enhance_meet_uri_is_not_available_to_download(self, s3_helper_mocked, empty_zoom_file_tracker):
        """
        Attribute error when meet binary is not available for downloading due to file does not exist or is not found
        """
        meet_uri = "6429324446"
        empty_zoom_file_tracker["meets"] = [meet_uri]
        zoom_files_tracker = dataclass_wizard.fromdict(ZoomFilesTracker, empty_zoom_file_tracker)
        media_controller = MediaController(zoom_file_tracker=zoom_files_tracker)
        with pytest.raises(AttributeError) as error:
            _ = media_controller.enhance(meet_uri_to_enhance=meet_uri)
        assert error.typename == "AttributeError"
        assert error.value.args[0] == "'NoneType' object has no attribute 'decode'"

    @patch.object(
        S3Helper,
        "get_file_content",
        return_value=json.dumps(s3_returned_inbound_call_object).encode("utf-8"),
    )
    @patch.object(S3Helper, "write_file_to_s3", side_effect=Exception("Mocked error when uploading binary"))
    def test_enhance_call_s3_upload_error(
        self,
        s3_helper_mocked,
        s3_helper_exception_uploader,
        empty_zoom_file_tracker,
    ):
        """
        Test when upload new object into bucket raised a exception for call
        """
        call_uri = "a6df2784-9ec4-43ce-8845-13275c55da40"
        empty_zoom_file_tracker["calls"] = [call_uri]
        zoom_files_tracker = dataclass_wizard.fromdict(ZoomFilesTracker, empty_zoom_file_tracker)
        media_controller = MediaController(zoom_file_tracker=zoom_files_tracker)
        with pytest.raises(Exception) as error:
            _ = media_controller.enhance(call_uri_to_enhance=call_uri)
        assert error.typename == "Exception"
        assert error.value.args[0] == "Mocked error when uploading binary"

    @patch.object(
        S3Helper,
        "get_file_content",
        return_value=json.dumps(s3_returned_meet_na_vtt).encode("utf-8"),
    )
    @patch.object(S3Helper, "write_file_to_s3", side_effect=Exception("Mocked error when uploading binary"))
    def test_enhance_meet_s3_upload_error(
        self,
        s3_helper_mocked,
        s3_helper_exception_uploader,
        empty_zoom_file_tracker,
    ):
        """
        Test when upload new object into bucket raised a exception for Meet
        """
        meet_uri = "6429324446"
        empty_zoom_file_tracker["meets"] = [meet_uri]
        zoom_files_tracker = dataclass_wizard.fromdict(ZoomFilesTracker, empty_zoom_file_tracker)
        media_controller = MediaController(zoom_file_tracker=zoom_files_tracker)
        with pytest.raises(Exception) as error:
            _ = media_controller.enhance(meet_uri_to_enhance=meet_uri)
        assert error.typename == "Exception"
        assert error.value.args[0] == "Mocked error when uploading binary"

    def test_vtt_parser_webvtt_to_list_ok(self):
        """
        Test Helper method to transform string to list of string to be parsed
        """
        result = _webvtt_to_list(transcript_ok_vtt)
        assert result
        assert isinstance(result, list)

        for entry in result:
            match = re.search(pattern=self.PATTERN_FOR_VTT, string=entry)
            assert match is not None

    @pytest.mark.parametrize(
        "transcript_input",
        [
            None,
            "",
            "asdfasdf",
            1234,
        ],
    )
    def test_vtt_parser_webvtt_to_list_not_ok(self, transcript_input):
        """
        Test Helper method to transform string to list of string to be parsed, but it fails and return empty list
        """
        if isinstance(transcript_input, int) or transcript_input is None:
            with pytest.raises(AttributeError) as error:
                _ = _webvtt_to_list(transcript_input)
            assert error.typename == "AttributeError"
        else:
            result = _webvtt_to_list(transcript_input)
            assert isinstance(result, list)
            assert len(result) == 0

    def test_vtt_parser(self):
        """
        Test for webvtt_parse_content which parse string into =>
        {
          'text': text,
          'end_ts': end_ts,
          'ts': start_ts,
          'speaker': speaker,
        }
        """
        result = webvtt_parse_content(transcript_ok_vtt)
        assert isinstance(result, dict)
        for entry in result["content"]:
            assert isinstance(entry, dict)
            assert 4 == len(entry.keys())
            assert "text" in entry.keys()
            assert "end_ts" in entry.keys()
            assert "ts" in entry.keys()
            assert "speaker" in entry.keys()

        assert True

    @pytest.mark.parametrize(
        "transcript_input",
        [
            None,
            "",
            "asdfasdf",
            1234,
        ],
    )
    def test_vtt_parser_exception_raised(self, transcript_input):
        """
        Test for webvtt_parse_content with invalid inputs
        """
        if isinstance(transcript_input, str):
            result = _webvtt_to_list(transcript_input)
            assert len(result) == 0
        else:
            with pytest.raises(AttributeError) as error:
                _ = _webvtt_to_list(transcript_input)
            assert error.typename == "AttributeError"
