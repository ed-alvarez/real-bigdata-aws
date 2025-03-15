"""
Test suite for lambda function extract blobs
"""
import logging
from unittest import mock
from unittest.mock import patch

import pytest
from moto import mock_lambda, mock_s3

import zoom_ingest
from zoom_ingest.zoom_functions.zoom_extract_blobs import lambda_handler
from zoom_ingest.zoom_shared.api_client import ZoomAPI
from zoom_ingest.zoom_tests.test_resources.test_zoom_functions_resources import (
    mocked_download_call_transcript,
    mocked_list_calls_logs,
    mocked_list_meeting_recordings,
    mocked_list_meetings_recordings,
    mocked_list_meetings_recordings_empty,
    mocked_list_phone_recordings_cf27,
    mocked_list_users,
    mocked_meeting_detail_8702,
    mocked_meeting_participants,
    mocked_user_detail,
)


def side_effect_for_list_phone_recordings(*args, **kwargs):
    if mocked_list_phone_recordings_cf27.get("call_log_id") in args:
        return mocked_list_phone_recordings_cf27
    else:
        return {}


def side_effect_for_meeting_details(*args, **kwargs):
    if mocked_meeting_detail_8702.get("id") in args:
        return mocked_meeting_detail_8702
    else:
        return {}


class TestLambdaExtractBlobs:
    PAYLOAD = "Payload"

    @mock_lambda
    @patch.object(ZoomAPI, "list_calls_logs", return_value=mocked_list_calls_logs)
    @patch.object(ZoomAPI, "call_download_transcript", return_value=mocked_download_call_transcript)
    @patch.object(ZoomAPI, "list_users", return_value=mocked_list_users)
    @patch.object(ZoomAPI, "generate_meetings_with_recordings", return_value=mocked_list_meetings_recordings)
    @patch.object(ZoomAPI, "user_detail", return_value=mocked_user_detail)
    @patch.object(ZoomAPI, "list_phone_recordings", side_effect=side_effect_for_list_phone_recordings)
    @patch.object(ZoomAPI, "meeting_detail", side_effect=side_effect_for_meeting_details)
    @patch.object(ZoomAPI, "past_meeting_participants", return_value=mocked_meeting_participants)
    @patch.object(ZoomAPI, "list_meeting_recordings", return_value=mocked_list_meeting_recordings)
    @pytest.mark.parametrize(
        "calls, meets",
        [
            (["cf27f361-606d-46d2-be78-0367727636b0"], []),
            ([], [87025065483, 81261751463]),
            (
                ["eaf1f9ea-2033-4a9d-9388-48744b4221ce"],
                ["todo.zoom/2022-09-17/raw_meet_87025065483_1663448557723"],
            ),
            (["cf27f361-606d-46d2-be78-0367727636b0"], [87025065483]),
        ],
    )
    def test_lambda_extraction_succeed_in_different_cartesian_product(
        self,
        list_calls_logs,
        call_download_transcript,
        list_users,
        list_meetings_recordings,
        user_detail,
        list_phone_recordings,
        meeting_detail,
        past_meeting_participants,
        list_meeting_recordings,
        calls,
        meets,
    ):
        """
        When the quantity of elements is different between calls or meets, lambda will process what is available.
        """
        event = {
            "Payload": {
                "customer": "melqart",
                "period": "custom",
                "if_error": "",
                "start_date": "2022-09-16",
                "end_date": "2022-09-17",
                "bucket_name": "todo",
                "success_step": False,
                "done_workflow": False,
                "calls": calls,
                "meets": meets,
            },
        }
        result = {}
        is_success_step_done = False
        while is_success_step_done is False:
            with mock_s3():
                result = lambda_handler(event=event, context={})
                event = {"Payload": result}
                is_success_step_done = event.get("Payload", {}).get("success_step")

        assert is_success_step_done
        assert result
        for call in result["calls"]:
            assert "raw" in call
        for meet in result["meets"]:
            assert "raw" in meet

    @mock_s3
    @mock_lambda
    def test_empty_input_event(self):
        result = lambda_handler(event={}, context={})
        assert result.get("error") == "'Payload'"

    @mock_s3
    @mock_lambda
    @patch.object(ZoomAPI, "list_calls_logs", return_value=mocked_list_calls_logs)
    @patch.object(ZoomAPI, "call_download_transcript", return_value=mocked_download_call_transcript)
    @patch.object(ZoomAPI, "list_users", return_value=mocked_list_users)
    @patch.object(ZoomAPI, "list_meetings_recordings", return_value=mocked_list_meetings_recordings_empty)
    def test_empty_payload_input_event(
        self,
        list_calls_logs,
        call_download_transcript,
        list_users,
        list_meetings_recordings,
    ):
        result = lambda_handler(event={"Payload": {}}, context={})
        assert result.get("success_step", False) is True
        assert len(result.get("calls")) == 0
        assert len(result.get("meets")) == 0

    @mock_s3
    @mock_lambda
    @patch.object(ZoomAPI, "list_calls_logs", return_value=mocked_list_calls_logs)
    @patch.object(ZoomAPI, "call_download_transcript", return_value=mocked_download_call_transcript)
    @patch.object(ZoomAPI, "list_users", return_value=mocked_list_users)
    @patch.object(ZoomAPI, "list_meetings_recordings", return_value=mocked_list_meetings_recordings_empty)
    def test_invalid_date_format(
        self,
        list_calls_logs,
        call_download_transcript,
        list_users,
        list_meetings_recordings,
        caplog,
    ):
        event = {
            "Payload": {
                "customer": "melqart",
                "period": "custom",
                "if_error": "",
                "start_date": "22/999/99",
                "end_date": "22/999/98",
                "bucket_name": "todo",
                "success_step": False,
                "done_workflow": False,
                "calls": ["eaf1f9ea-2033-4a9d-9388-48744b4221ce"],
                "meets": [87025065483],
            },
        }
        with caplog.at_level(logging.INFO):
            result = lambda_handler(event=event, context={})
            assert "time data '22/999/99' does not match format '%Y-%m-%d'" in caplog.text
        assert result

    @mock_s3
    @mock_lambda
    def test_exception_is_raised(self):
        exception_message = "Exception for Zoom API"
        zoom_ingest.zoom_functions.zoom_extract_blobs.handler.extract_blobs = mock.Mock(
            side_effect=Exception(exception_message),
        )
        mock.MagicMock(name="method")
        result = lambda_handler(event={"Payload": {}}, context={})
        assert result.get("error") == exception_message
