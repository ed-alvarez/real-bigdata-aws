from datetime import datetime, timedelta
from unittest import mock
from unittest.mock import patch

import pytest
from moto import mock_lambda, mock_s3

import zoom_ingest
from zoom_ingest.zoom_functions.zoom_create_ids import lambda_handler
from zoom_ingest.zoom_shared.api_client import ZoomAPI
from zoom_ingest.zoom_tests.test_resources.test_zoom_functions_resources import (
    mocked_download_call_transcript,
    mocked_list_calls_logs,
    mocked_list_calls_logs_empty,
    mocked_list_meetings_recordings,
    mocked_list_meetings_recordings_empty,
    mocked_list_users,
)


@pytest.fixture()
def daily_event_no_date():
    return {"client": "melqart", "period": "daily"}


@pytest.fixture()
def custom_event_with_date():
    return {
        "client": "melqart",
        "period": "custom",
        "start_date": "2022-09-16",
        "end_date": "2022-09-17",
    }


@pytest.fixture()
def error_event_process():
    return {"wrong": "noclient", "date_range": "daily", "bucket_name": "todo.dev"}


@mock_s3
@mock_lambda
class TestLambdaCreateIds:

    date_pattern = "%Y-%m-%d"
    yesterday = (datetime.now() - timedelta(days=1)).strftime(date_pattern)
    today = datetime.now().strftime(date_pattern)

    @patch.object(ZoomAPI, "list_calls_logs", return_value=mocked_list_calls_logs)
    @patch.object(ZoomAPI, "call_download_transcript", return_value=mocked_download_call_transcript)
    @patch.object(ZoomAPI, "list_users", return_value=mocked_list_users)
    @patch.object(ZoomAPI, "list_meetings_recordings", return_value=mocked_list_meetings_recordings_empty)
    def test_handler_daily_only_call(
        self,
        list_calls_logs,
        call_download_transcript,
        list_users,
        list_meetings_recordings,
        daily_event_no_date,
    ):
        context = {}
        result = lambda_handler({"Payload": daily_event_no_date}, context)

        assert isinstance(result, dict)
        assert result["success_step"] is True
        assert result["period"] == "daily"
        assert self.yesterday == result["start_date"]
        assert self.today == result["end_date"]
        assert result["calls"]
        assert len(result["calls"]) > 0
        assert mocked_list_calls_logs[0]["id"] == result["calls"][0]
        for call in result["calls"]:
            assert isinstance(call, str)

    @patch.object(ZoomAPI, "list_calls_logs", return_value=mocked_list_calls_logs_empty)
    @patch.object(ZoomAPI, "call_download_transcript", return_value=mocked_download_call_transcript)
    @patch.object(ZoomAPI, "list_users", return_value=mocked_list_users)
    @patch.object(ZoomAPI, "generate_meetings_with_recordings", return_value=mocked_list_meetings_recordings)
    def test_handler_daily_only_meet(
        self,
        list_calls_logs,
        call_download_transcript,
        list_users,
        list_meetings_recordings,
        daily_event_no_date,
    ):
        context = {}
        result = lambda_handler({"Payload": daily_event_no_date}, context)

        assert isinstance(result, dict)
        assert result["success_step"] is True
        assert result["period"] == "daily"
        assert self.yesterday == result["start_date"]
        assert self.today == result["end_date"]
        assert result["meets"]
        assert 2 == len(result["meets"])
        for meet in result["meets"]:
            assert isinstance(meet, int)

    @patch.object(ZoomAPI, "list_calls_logs", return_value=mocked_list_calls_logs)
    @patch.object(ZoomAPI, "call_download_transcript", return_value=mocked_download_call_transcript)
    @patch.object(ZoomAPI, "list_users", return_value=mocked_list_users)
    @patch.object(ZoomAPI, "generate_meetings_with_recordings", return_value=mocked_list_meetings_recordings)
    def test_handler_daily_with_call_and_meet(
        self,
        list_calls_logs,
        call_download_transcript,
        list_users,
        list_meetings_recordings,
        daily_event_no_date,
    ):
        context = {}
        result = lambda_handler({"Payload": daily_event_no_date}, context)

        assert isinstance(result, dict)
        assert result["success_step"] is True
        assert result["period"] == "daily"
        assert self.yesterday == result["start_date"]
        assert self.today == result["end_date"]
        assert result["calls"]
        assert len(result["calls"]) > 0
        assert mocked_list_calls_logs[0]["id"] == result["calls"][0]
        for call in result["calls"]:
            assert isinstance(call, str)
        assert result["meets"]
        assert 2 == len(result["meets"])
        for meet in result["meets"]:
            assert isinstance(meet, int)

    @patch.object(ZoomAPI, "list_calls_logs", return_value=mocked_list_calls_logs)
    @patch.object(ZoomAPI, "call_download_transcript", return_value=mocked_download_call_transcript)
    @patch.object(ZoomAPI, "list_users", return_value=mocked_list_users)
    @patch.object(ZoomAPI, "generate_meetings_with_recordings", return_value=mocked_list_meetings_recordings)
    def test_handler_with_dates(
        self,
        list_calls_logs,
        call_download_transcript,
        list_users,
        list_meetings_recordings,
        custom_event_with_date,
    ):
        context = {}
        result = lambda_handler({"Payload": custom_event_with_date}, context)
        assert type(result) == dict
        assert result["success_step"] is True
        assert custom_event_with_date["start_date"] == result["start_date"]
        assert custom_event_with_date["end_date"] == result["end_date"]

    def test_handler_wrong_payload(self, error_event_process):
        context = {}
        result = lambda_handler({"wrong": error_event_process}, context)
        assert result["success_step"] is False

    def test_handler_exceptio_zoom_api(self, custom_event_with_date):
        context = {}
        ZoomAPI.list_calls_logs = mock.Mock(side_effect=Exception("Exception for Zoom Ingest"))
        mock.MagicMock(name="method")
        result = lambda_handler({"Payload": custom_event_with_date}, context)
        assert type(result) == dict
        assert result["success_step"] is False
        assert result["error"] == "asdict() should be called on dataclass instances"

    def test_failure_extract_ids_from_api(self, custom_event_with_date):
        context = {}
        zoom_ingest.zoom_functions.zoom_create_ids.handler.extract_ids_from_api = mock.Mock(
            side_effect=Exception("Exception to extract ids"),
        )
        mock.MagicMock(name="method")
        result = lambda_handler({"Payload": custom_event_with_date}, context)
        assert type(result) == dict
        assert result["success_step"] is False
