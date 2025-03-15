import os
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, Mock, patch

import pytest

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_src.teams_data_download.download_user_list import GrabUserTeamIDs
from teams_src.teams_data_download.user_chats_process import IngestUsersToProcess
from teams_src.teams_shared_modules.teams_data_classes import TeamsDateRange
from teams_tests.data.stepfunction_data import teams_history_event
from teams_tests.data.user_ids import expected_user_ids

AWS_REGION = os.environ.get("AWS_Region", "eu-west-1")

CLIENT_NAME = "test-ips"
BUCKET_NAME = f"{CLIENT_NAME}.ips"

teams_date_range: TeamsDateRange = TeamsDateRange()
teams_date_range.search_from = datetime(2021, 1, 14, 00, 00, 00)
teams_date_range.search_to = datetime(2021, 1, 13, 00, 00, 00)


class TestFunctions:
    @pytest.fixture
    def user_ids(self):
        return {"user_ids": "541e7d82-ea07-43e4-8168-115c609569ae"}

    @contextmanager
    def s3_setup(self, s3_client):
        bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": AWS_REGION})
        yield

    @patch.object(
        IngestUsersToProcess,
        "get_user_list",
        return_value=[expected_user_ids],
    )
    def test_getting_users_ids(self, get_user_list_mocked, dynamo_db_teams_setup, user_ids, teams_ddb_client):
        with patch("teams_settings.UPLOAD_TO_ES", False):
            with mock.patch(
                "teams_src.teams_shared_modules.teams_data_classes.DynamoClientRecord.ddb_client",
                teams_ddb_client,
            ):
                obj_one_to_one_chats: GrabUserTeamIDs = GrabUserTeamIDs(
                    event=teams_history_event, dynamo_client_record=dynamo_db_teams_setup
                )
                s3_mock = MagicMock()
                s3_mock.lamda_write_to_s3 = Mock(return_value=None)
                response = obj_one_to_one_chats.get_users_ids(s3_mock)
                assert response == [user_ids]

    def test_event_date_with_wrong_date_format(self):
        """
        Test the result when the event dates are in wrong format
        """
        # TODO
        pass

    def test_result_on_workflow_failure(self):
        """
        Check the result when there is an unexpected error raised
        """
        # TODO
        pass

    def test_empty_users_list(self):
        """
        Check the result when there are any user list found
        """
        # TODO
        pass
