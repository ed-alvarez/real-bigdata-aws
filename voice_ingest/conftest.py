from contextlib import contextmanager

import botocore
import botocore.session
import pytest
from botocore.stub import Stubber

CLIENT_NAME = "testing"
BUCKET_NAME = f"{CLIENT_NAME}.ips"


@pytest.fixture(autouse=True)
def transcribe_stub():
    transcribe = botocore.session.get_session().create_client("transcribe")
    with Stubber(transcribe) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()


@contextmanager
def ddb_voice_setup(dynamo_client):
    table = dynamo_client.create_table(
        TableName="dev_voiceIngest",
        KeySchema=[
            {"AttributeName": "transcriptionJob", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[{"AttributeName": "transcriptionJob", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )
    # table.meta.client.get_waiter('table_exists').wait(TableName=DYNAMO_DB_TABLE)
    yield


@pytest.fixture
def dynamo_db_voice_setup(ddb_client):
    result = ddb_voice_setup(dynamo_client=ddb_client)
    yield result


@contextmanager
def parameters_voice_setup(ssm_client):
    ssm_client.put_parameter(
        Name=f"/{CLIENT_NAME}/voice/cdr_type",
        Description="CDR Type",
        Value="ringcentral",
        Type="String",
    )

    ssm_client.put_parameter(
        Name=f"/{CLIENT_NAME}/voice/transcribe_type",
        Description="Audio Transcript Type",
        Value="speaker",
        Type="String",
    )
    yield


@pytest.fixture
def ssm_voice_setup(ssm_client):
    result = parameters_voice_setup(ssm_client=ssm_client)
    yield result
