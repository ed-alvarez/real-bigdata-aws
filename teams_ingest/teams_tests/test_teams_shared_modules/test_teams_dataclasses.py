import sys
from pathlib import Path
from unittest import mock

from dotenv import load_dotenv

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_src.teams_shared_modules.teams_data_classes import (
    ClientCreds,
    DynamoClientRecord,
)

from teams_ingest.conftest import ddb_teams_setup

load_dotenv()


class TestDynamoClientRecord:
    def test_create_dynamo_client_record(self, teams_ddb_client, dynamo_db_teams_setup):
        with mock.patch(
            "teams_src.teams_shared_modules.teams_data_classes.DynamoClientRecord.ddb_client",
            teams_ddb_client,
        ):
            record: DynamoClientRecord = DynamoClientRecord(client="test-ips").get_dynamo_client()
            assert "TEST-DATA@ip-sentinel.com" in record.excluded


class TestClientCreds:
    def test_create_client_creds_record(self, ssm_teams_setup):
        with ssm_teams_setup:
            record: ClientCreds = ClientCreds(firm="test-ips", tenant_id="0000-0000-0000-0000")
        assert record.secret == "no-app-secret"
