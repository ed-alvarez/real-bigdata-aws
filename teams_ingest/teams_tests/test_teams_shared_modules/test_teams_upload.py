import os
import re
import sys
from contextlib import contextmanager
from dataclasses import asdict
from json import dumps
from pathlib import Path
from typing import Dict
from unittest import mock

import pytest
import responses
from mock import patch

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_settings import eventPeriod, eventSource
from teams_src.teams_shared_modules.step_funtion_data_classes import TeamsDecode
from teams_tests.data.teams_data_1_day import result1

AWS_REGION = os.environ.get("AWS_Region", "eu-west-1")
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

teams_env_path = f"{BASE_DIR}/teams_ingest/.env"

CLIENT_NAME = "test-ips"
BUCKET_NAME = f"{CLIENT_NAME}.ips"
TENANT_NAME = "test-ips"
TENANT_ID = os.environ.get("TEST_CHANNEL", "xxxx")
file_key = "dev.todo.teams/2021-06-10/test-ips_all_one_to_one_chats.json"
aws_event: TeamsDecode = TeamsDecode(
    firm=CLIENT_NAME,
    period=eventPeriod.daily.value,
    tenant_id=TENANT_ID,
    tenant_name=TENANT_NAME,
)
aws_event.list_of_files_to_process = [file_key]
aws_event_dict: Dict = asdict(aws_event)

from shared.shared_src.es.es_client import ElasticSearchClient


class TestFunctions:
    @contextmanager
    def s3_setup(self, s3_client):
        bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": AWS_REGION})

        s3_client.put_object(Body=str(dumps(result1)), Bucket=BUCKET_NAME, Key=file_key)

        yield

    @patch.object(ElasticSearchClient, "get_client")
    def test_teams_upload(
        self,
        mocked_get_client,
        teams_s3_client,
        test_lambda_context,
        dynamo_db_teams_setup,
        ssm_teams_setup,
        teams_ddb_client,
    ):
        with patch("teams_settings.UPLOAD_TO_ES", False):
            with mock.patch(
                "teams_src.teams_shared_modules.teams_data_classes.DynamoClientRecord.ddb_client",
                teams_ddb_client,
            ):
                with self.s3_setup(teams_s3_client):
                    with responses.RequestsMock() as rsps:
                        rsps.add_passthru(re.compile("https://login.microsoftonline.com*"))
                        rsps.add_passthru(re.compile("https://graph.microsoft.com*"))
                        rsps.add_passthru(re.compile("https://ipsentinelltd-my.sharepoint.com*"))
                        rsps.add_passthru(re.compile("http://localhost*"))
                        with ssm_teams_setup:
                            from teams_src.teams_data_processing_and_ingest import (
                                user_chat_to_conversation,
                            )
                            from teams_src.teams_data_processing_and_ingest.teams_upload import (
                                TeamsUpload,
                            )

                            with patch.object(user_chat_to_conversation, "UPLOAD_TO_ES", False):
                                teams_upload_obj: TeamsUpload = TeamsUpload(aws_event=aws_event_dict, aws_context=test_lambda_context)
                                response = teams_upload_obj.teams_ingest_workflow()
                                assert response
