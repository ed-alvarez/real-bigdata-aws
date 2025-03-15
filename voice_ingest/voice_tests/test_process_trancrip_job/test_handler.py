from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import pytest
from dateutil.tz import tzlocal
from voice_settings import DYNAMO_DB_TABLE
from voice_src.process_transcript_job.handler import lambda_handler
from voice_tests.test_data.events.Cloudwatch_data import transcribe_event

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CLIENT_NAME = "ips"
BUCKET_NAME = f"{CLIENT_NAME}.ips"
DIRECTORY = "todo.voice/2021-03-09/"

transciption_file_location = f"{BASE_DIR}/voice_tests/test_data/thetalake_ringcentral/speaker_ident/test-2020-06-25.f0f5cba1-a457-4f44-edb8-12def04cd9e0-1593875883-433154.json"
transcription_file_key = f"{DIRECTORY}ips-2021-03-09.13837a13-9049-70c6-8123-545eebc42abd-1615834524-443608.json"
transcription_job_id = "ips-2021-03-09.13837a13-9049-70c6-8123-545eebc42abd-1615834524-443608"

audio_file_location = f"{BASE_DIR}/voice_tests/test_data/thetalake_ringcentral/2020-06-25.f0f5cba1-a457-4f44-edb8-12def04cd9e0.mp3"
audio_file_key = f"{DIRECTORY}2021-03-09.13837a13-9049-70c6-8123-545eebc42abd.mp3"

cdr_file_location = f"{BASE_DIR}/voice_tests/test_data/thetalake_ringcentral/2020-06-25.meta.f0f5cba1-a457-4f44-edb8-12def04cd9e0.json"
cdr_file_key = f"{DIRECTORY}2021-03-09.meta.13837a13-9049-70c6-8123-545eebc42abd.xml"


class TestFunction:
    @contextmanager
    def s3_setup(self, s3_client):
        bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": "eu-west-1"})

        with open(transciption_file_location, "rb") as f:
            s3_client.upload_fileobj(f, BUCKET_NAME, transcription_file_key)

        with open(audio_file_location, "rb") as f:
            s3_client.upload_fileobj(f, BUCKET_NAME, audio_file_key)

        with open(cdr_file_location, "rb") as f:
            s3_client.upload_fileobj(f, BUCKET_NAME, cdr_file_key)

        yield

    @contextmanager
    def ddb_setup(self, dynamo_client):
        table = dynamo_client.create_table(
            TableName=DYNAMO_DB_TABLE,
            KeySchema=[
                {"AttributeName": "transcriptionJob", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[{"AttributeName": "transcriptionJob", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )
        # table.meta.client.get_waiter('table_exists').wait(TableName=DYNAMO_DB_TABLE)
        yield

    def populate_dynamo(self):
        from voice_src.helpers.helper_dataclass import DynamoTranscriptionRecord

        start_time = datetime(2021, 3, 9, 14, 56, 22, 88000, tzinfo=tzlocal())
        object: DynamoTranscriptionRecord = DynamoTranscriptionRecord(client=CLIENT_NAME, audioFileKey=audio_file_key)

        object.transcriptionJob = transcription_job_id
        object.transcriptionStartTime = start_time
        object.generate_data()
        object.generate_cdr_file_key()
        object.generate_transcription_file_key()
        object.put_dynamo_transcription_job()
        return

    invalid_event = {
        "detail": {
            "TranscriptionJobName": transcription_job_id,
            "TranscriptionJobStatus": "FAILED",
            "FailureReason": "The input media file length is too small. Minimum audio duration is 0.500000 milliseconds. Check the length of the file and try your request again.",
        }
    }

    test_1 = (transcribe_event(transcription_job_id), True)
    test_2 = (invalid_event, False)

    CASES = [test_1, test_2]

    @pytest.mark.parametrize("event, expected", CASES)
    def test_lambda_handler(self, event, expected, s3_client, ddb_client, test_lambda_context):
        with self.s3_setup(s3_client):
            with self.ddb_setup(ddb_client):
                self.populate_dynamo()
                response = lambda_handler(event, test_lambda_context)
                assert response
