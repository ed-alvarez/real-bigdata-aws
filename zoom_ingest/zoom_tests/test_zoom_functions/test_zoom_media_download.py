import json
from unittest.mock import patch

import boto3 as boto3
import pytest
from moto import mock_lambda, mock_s3

from zoom_ingest.zoom_functions.zoom_media_download import lambda_handler
from zoom_ingest.zoom_shared.api_client import ZoomAPI
from zoom_ingest.zoom_tests.test_resources.test_zoom_functions_resources import (
    mocked_download_endpoint,
    mocked_enhanced_call_zoomdto,
    mocked_put_call_object,
    mocked_put_meet_object,
)

call_key = "todo.zoom/2022-10-09/raw_call_cf27f361-606d-46d2-be78-0367727636b0_1665369165050.json"
meet_key = "todo.zoom/2022-09-17/raw_meet_87025065483_1663448557723"


@pytest.fixture()
def daily_event_no_date():
    return {
        "customer": "melqart",
        "bucket_name": "todo.zoom",
        "success_step": True,
        "done_workflow": False,
        "calls": [call_key],
        "meets": [meet_key],
    }


@pytest.fixture()
def enhanced_call_zoomdto():
    return mocked_enhanced_call_zoomdto


@mock_s3
@mock_lambda
class TestLambdaMediaDownload:
    def put_mocked_objects(self):
        s3 = boto3.client("s3", region_name="eu-west-1")
        bucket_name = "dev-melqart.ips"
        s3.create_bucket(Bucket=bucket_name)
        dict_meet_body = mocked_put_meet_object
        dict_call_body = mocked_put_call_object
        s3.put_object(
            Body=bytes(json.dumps(dict_call_body).encode("utf-8")),
            Bucket=bucket_name,
            Key=call_key,
        )
        s3.put_object(
            Body=bytes(json.dumps(dict_meet_body).encode("utf-8")),
            Bucket=bucket_name,
            Key=meet_key,
        )

    @patch.object(ZoomAPI, "download_endpoint", return_value=mocked_download_endpoint)
    def test_download_call_and_meet(
        self,
        download_endpoint,
        enhanced_call_zoomdto,
        daily_event_no_date,
    ):
        self.put_mocked_objects()
        context = {}
        result = lambda_handler({"Payload": daily_event_no_date}, context)

        assert isinstance(result, dict)
        assert result["success_step"] is True
        assert len(result["calls"]) == 1
        assert len(result["meets"]) == 1
        for call in result["calls"]:
            assert "ready" in call
        for meet in result["meets"]:
            assert "ready" in meet

    def test_download_call_and_meet_but_missing_objects(self, daily_event_no_date):
        context = {}
        result = lambda_handler({"Payload": daily_event_no_date}, context)

        assert isinstance(result, dict)
        assert result["success_step"] is False
        assert result["period"] == "daily"
        assert len(result["calls"]) == 0
        # since calls fails, it performs an early return and meets was not processed OJO, try second or N iter
        assert len(result["meets"]) == 1

    @pytest.mark.parametrize(
        "payload, success_step",
        [
            (None, False),
            ({}, True),
            ({"a": 1}, True),
            (1, False),
        ],
    )
    def test_media_download_invalid_payload(self, payload, success_step):
        context = {}
        result = lambda_handler({"Payload": payload}, context)
        assert result["success_step"] is success_step
