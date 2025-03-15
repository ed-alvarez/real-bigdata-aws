from unittest import mock

import pytest

from teams_src.HackDynamo.MyDynamo import MyDynamo
from moto import mock_dynamodb
import boto3


@pytest.fixture
def get_mocked_dynamo_with_inserted_table(teams_ddb_client):
    TestMyDynamo.create_db_table()


class TestMyDynamo:

    @staticmethod
    def create_db_table(dynamo_client=None):
        if dynamo_client is None:
            dynamo_client = boto3.client("dynamodb")
        dynamo_client.create_table(
            TableName="basicSongsTable",
            AttributeDefinitions=[
                {
                    "AttributeName": "artist",
                    "AttributeType": "S"
                },
                {
                    "AttributeName": "song",
                    "AttributeType": "S"
                }
            ],
            KeySchema=[
                {
                    "AttributeName": "artist",
                    "KeyType": "HASH"
                },
                {
                    "AttributeName": "song",
                    "KeyType": "RANGE"
                }
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 1,
                "WriteCapacityUnits": 1
            }
        )

    def test_mydynamo(self):
        with mock_dynamodb():
            my_dynamo = MyDynamo()
            TestMyDynamo.create_db_table()
            assert len(my_dynamo.list_all_tables()['TableNames']) == 1

    def test_mydynamo_with_fixture_from_conftest(self, teams_ddb_client):
        my_dynamo = MyDynamo()
        TestMyDynamo.create_db_table()
        assert len(my_dynamo.list_all_tables()['TableNames']) == 1

    def test_mydynamo_with_module_fixture(self, get_mocked_dynamo_with_inserted_table, teams_ddb_client):
        with mock.patch(
                'teams_src.teams_shared_modules.teams_data_classes.DynamoClientRecord.ddb_client'
                , teams_ddb_client
        ):
            my_dynamo = MyDynamo()
            assert len(my_dynamo.list_all_tables()['TableNames']) == 1

    @mock_dynamodb
    def test_mydynamo_using_dynamo_setup_fixture(self):
        """USING THIS FIXTURE FROM CONFTEST IS NOT WORKING, SO LEN() OF TABLES IS 0"""
        my_dynamo = MyDynamo()
        assert len(my_dynamo.list_all_tables()['TableNames']) == 0

    def test_mydynamo_using_dynamo_setup_fixture_no_context(self, dynamo_db_teams_setup_no_context):
        """USING THIS FIXTURE FROM CONFTEST IS WORKING, SO LEN() OF TABLES IS 1"""
        my_dynamo = MyDynamo()
        assert len(my_dynamo.list_all_tables()['TableNames']) == 1
