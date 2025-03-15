import json
import os
from contextlib import contextmanager
from pathlib import Path

import boto3
import pytest
from moto import mock_dynamodb, mock_s3, mock_ssm

BASE_DIR = Path(__file__).resolve().parent


@pytest.fixture()
def context_param():
    class Context:
        def __init__(self):
            self.aws_request_id = "test_aws_uuid"

    return Context()


@pytest.fixture()
def launch_event_daily():
    return {"firm": "test_client", "tenant_name": "test_tenant", "source": "test", "period": "daily"}


@pytest.fixture()
def launch_event_historical():
    return {
        "firm": "test_client",
        "tenant_name": "test_tenant",
        "source": "test",
        "period": "historical",
        "start_date": "2022-01-01",
        "end_date": "2022-01-31",
    }


@pytest.fixture
def state_machine_creator(step_fn_client):
    state_machine_definition = {"StartAt": "Start", "States": {"Start": {"Type": "Pass", "End": True}}}
    response = step_fn_client.create_state_machine(
        name="TestStateMachine",
        definition=json.dumps(state_machine_definition),
        roleArn="arn:aws:iam::123456789012:role/service-role/StatesExecutionRole-eu-west-1",
    )
    return response["stateMachineArn"]


def ddb_teams_setup(dynamodb_client):
    result = dynamodb_client.create_table(
        TableName="dev-msTeamsIngest",
        KeySchema=[{"AttributeName": "client", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "client", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    response = dynamodb_client.put_item(
        TableName="dev-msTeamsIngest",
        Item={
            "client": {"S": "test-ips"},
            "excluded": {
                "SS": [
                    "TEST-DATA@ip-sentinel.com",
                    "chris@ip-sentinel.com",
                    "dan@ip-sentinel.com",
                    "filereader@ip-sentinel.com",
                    "filewriter@ip-sentinel.com",
                    "ipsentinel@ip-sentinel.com",
                    "steve@fingerprint-supervision.com",
                    "support@fingerprint-supervision.com",
                    "svc-jira@ip-sentinel.com",
                ]
            },
            "users": {
                "L": [
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682958"},
                            "iD": {"S": "28ad04f7-55d2-4fe8-b917-52f3c24ab13d"},
                            "uPN": {"S": "james@ip-sentinel.com"},
                        }
                    },
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682977"},
                            "iD": {"S": "49e7c390-85fc-43ea-8d94-797e2c23f04f"},
                            "uPN": {"S": "tom@ip-sentinel.com"},
                        }
                    },
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682979"},
                            "iD": {"S": "9d3a6f3c-0945-4a0f-a34a-035d33eff064"},
                            "uPN": {"S": "mike@ip-sentinel.com"},
                        }
                    },
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682981"},
                            "iD": {"S": "9a618be6-2988-4202-84cf-634ecc976bf2"},
                            "uPN": {"S": "sean@fingerprint-supervision.com"},
                        }
                    },
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682984"},
                            "iD": {"S": "0f97ac84-386f-41fe-9902-77beded8033a"},
                            "uPN": {"S": "brielle@fingerprint-supervision.com"},
                        }
                    },
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682986"},
                            "iD": {"S": "11c4fc5e-c6f9-4e4f-9f2c-f02642ec9c61"},
                            "uPN": {"S": "anthony@fingerprint-supervision.com"},
                        }
                    },
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682988"},
                            "iD": {"S": "30ae7014-45ce-44f3-9120-10ce89df14ce"},
                            "uPN": {"S": "robert@fingerprint-supervision.com"},
                        }
                    },
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682990"},
                            "iD": {"S": "0343ab0a-2dee-4672-bc86-20af382ea5d8"},
                            "uPN": {"S": "denny@fingerprint-supervision.com"},
                        }
                    },
                ]
            },
        },
    )


def ddb_teams_setup_no_context(dynamodb_client):
    result = dynamodb_client.create_table(
        TableName="dev-msTeamsIngest",
        KeySchema=[{"AttributeName": "client", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "client", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    response = dynamodb_client.put_item(
        TableName="dev-msTeamsIngest",
        Item={
            "client": {"S": "test-ips"},
            "excluded": {
                "SS": [
                    "TEST-DATA@ip-sentinel.com",
                    "chris@ip-sentinel.com",
                    "dan@ip-sentinel.com",
                    "filereader@ip-sentinel.com",
                    "filewriter@ip-sentinel.com",
                    "ipsentinel@ip-sentinel.com",
                    "steve@fingerprint-supervision.com",
                    "support@fingerprint-supervision.com",
                    "svc-jira@ip-sentinel.com",
                ]
            },
            "users": {
                "L": [
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682958"},
                            "iD": {"S": "28ad04f7-55d2-4fe8-b917-52f3c24ab13d"},
                            "uPN": {"S": "james@ip-sentinel.com"},
                        }
                    },
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682977"},
                            "iD": {"S": "49e7c390-85fc-43ea-8d94-797e2c23f04f"},
                            "uPN": {"S": "tom@ip-sentinel.com"},
                        }
                    },
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682979"},
                            "iD": {"S": "9d3a6f3c-0945-4a0f-a34a-035d33eff064"},
                            "uPN": {"S": "mike@ip-sentinel.com"},
                        }
                    },
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682981"},
                            "iD": {"S": "9a618be6-2988-4202-84cf-634ecc976bf2"},
                            "uPN": {"S": "sean@fingerprint-supervision.com"},
                        }
                    },
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682984"},
                            "iD": {"S": "0f97ac84-386f-41fe-9902-77beded8033a"},
                            "uPN": {"S": "brielle@fingerprint-supervision.com"},
                        }
                    },
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682986"},
                            "iD": {"S": "11c4fc5e-c6f9-4e4f-9f2c-f02642ec9c61"},
                            "uPN": {"S": "anthony@fingerprint-supervision.com"},
                        }
                    },
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682988"},
                            "iD": {"S": "30ae7014-45ce-44f3-9120-10ce89df14ce"},
                            "uPN": {"S": "robert@fingerprint-supervision.com"},
                        }
                    },
                    {
                        "M": {
                            "date_added": {"S": "2021-02-19T17:50:17.682990"},
                            "iD": {"S": "0343ab0a-2dee-4672-bc86-20af382ea5d8"},
                            "uPN": {"S": "denny@fingerprint-supervision.com"},
                        }
                    },
                ]
            },
        },
    )


@pytest.fixture
def dynamo_db_teams_setup(teams_ddb_client):
    ddb_teams_setup(dynamodb_client=teams_ddb_client)


@pytest.fixture
def dynamo_db_teams_setup_no_context(teams_ddb_client):
    ddb_teams_setup_no_context(teams_ddb_client)


@contextmanager
def parameters_teams_setup(secrets_client):
    secrets_client.put_parameter(
        Name="/teams/dev/app_id",
        Description="",
        Value=os.environ.get("APP_ID", "no-app-id"),
        Type="String",
    )

    secrets_client.put_parameter(
        Name="/teams/dev/app_secret",
        Description="",
        Value=os.environ.get("APP_SECRET", "no-app-secret"),
        Type="SecureString",
    )

    secrets_client.put_parameter(
        Name="/teams/test_client/test_tenant/TENANT_ID",
        Description="",
        Value="long_guid",
        Type="SecureString",
    )
    yield


@pytest.fixture
def ssm_teams_setup(teams_ssm_client):
    result = parameters_teams_setup(secrets_client=teams_ssm_client)
    yield result


@pytest.fixture
def teams_ddb_client():
    """Since Dynamodb fixture is not working from root conftest. We created a module fixgure"""
    with mock_dynamodb():
        conn = boto3.client("dynamodb")
        yield conn


@pytest.fixture
def teams_ssm_client():
    """Since SSM fixture is not working from root conftest. We created a module fixgure"""
    with mock_ssm():
        yield boto3.client("ssm")


@pytest.fixture
def teams_s3_client(aws_credentials):
    """Since SSM fixture is not working from root conftest. We created a module fixgure"""
    with mock_s3():
        yield boto3.client("s3")
