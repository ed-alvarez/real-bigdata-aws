import json
from unittest import mock
from unittest.mock import patch

import boto3 as boto3
import pytest
from moto import mock_lambda, mock_s3

import zoom_ingest
from shared.shared_src.es.es_dsl_client import ESUploadDSl
from zoom_ingest.zoom_functions.zoom_process import lambda_handler
from zoom_ingest.zoom_shared import zoom_es_parser
from zoom_ingest.zoom_tests.test_resources.test_zoom_functions_resources import (
    mocked_lambda_process_call_cf27,
)


@mock_lambda
class TestLambdaProcess:

    call_key_cf27 = "todo.zoom/2022-10-16/ready_call_cf27f361-606d-46d2-be78-0367727636b0_1665953213138.json"
    meet_key_87025065483 = "todo.zoom/2022-10-16/ready_meet_87025065483_1665953213496.json"

    def put_mocked_ready_objects(self):
        s3 = boto3.client("s3", region_name="eu-west-1")
        bucket_name = "dev-melqart.ips"
        s3.create_bucket(Bucket=bucket_name)
        dict_call_body = mocked_lambda_process_call_cf27
        dict_meet_body = {1: 1}
        s3.put_object(
            Body=bytes(json.dumps(dict_call_body).encode("utf-8")),
            Bucket=bucket_name,
            Key=self.call_key_cf27,
        )
        s3.put_object(
            Body=bytes(json.dumps(dict_meet_body).encode("utf-8")),
            Bucket=bucket_name,
            Key=self.meet_key_87025065483,
        )

    @pytest.mark.parametrize(
        "calls, meets",
        [
            (call_key_cf27, meet_key_87025065483),
        ],
    )
    def test_process_blob_and_pushed_to_es(self, calls, meets):
        event = {
            "Payload": {
                "customer": "melqart",
                "date_range": "daily",
                "bucket_name": "todo.zoom",
                "success_step": False,
                "done_workflow": False,
                "calls": [calls],
                "meets": [],
            },
        }
        with mock_s3():
            self.put_mocked_ready_objects()
            result = {}
            is_success_step_done = False
            while is_success_step_done is False:
                result = lambda_handler(event=event, context={})
                event = {"Payload": result}
                is_success_step_done = event.get("Payload", {}).get("success_step")

            assert result
            assert is_success_step_done

    def test_process_blob_invalid_payload(self):
        result = lambda_handler(event={}, context={})
        assert "Payload" in result["error"]

    @mock_s3
    @patch.object(ESUploadDSl, "insert_document", side_effect=Exception("Exception deleting item"))
    def test_process_blob_and_failed_to_push_to_es(
        self,
        insert_document,
    ):
        event = {
            "Payload": {
                "customer": "melqart",
                "date_range": "daily",
                "bucket_name": "todo.zoom",
                "success_step": False,
                "done_workflow": False,
                "calls": [self.call_key_cf27],
                "meets": [],
            },
        }
        self.put_mocked_ready_objects()
        result = {}
        is_success_step_done = False
        zoom_ingest.zoom_functions.zoom_process.handler.push_to_elastic_search = mock.Mock(
            side_effect=Exception("Exception for push_to_elastic_search"),
        )
        mock.MagicMock(name="method")
        while is_success_step_done is False:
            result = lambda_handler(event=event, context={})
            event = {"Payload": result}
            is_success_step_done = event.get("Payload", {}).get("success_step")
        assert event["Payload"]["success_step"] is True
        assert event["Payload"]["done_workflow"] is True
