# https://chase-seibert.github.io/blog/2015/06/25/python-mocking-cookbook.html
import datetime
from contextlib import contextmanager
from pathlib import Path

import boto3
import botocore.session
from botocore.stub import Stubber
from dateutil.tz import tzlocal
from mock import patch
from voice_src.create_transcription_job.handler import lambda_handler
from voice_tests.test_data.events.s3_event import create_event as s3_event

BASE_DIR = Path(__file__).resolve().parent.parent
CLIENT_NAME = "testing"
BUCKET_NAME = f"{CLIENT_NAME}.ips"
S3_AUDIO_FILE = "dev.todo.voice/2021-06-30/2021-06-30.134499-8f0b076f-5424-e795-7305-3867eadb2a9e.mp3"

Transcription_Response = {
    "CompletionTime": datetime.datetime(2021, 7, 1, 14, 28, 6, 896000, tzinfo=tzlocal()),
    "ContentRedaction": {"RedactionOutput": "string", "RedactionType": "string"},
    "CreationTime": datetime.datetime(2021, 7, 1, 14, 28, 6, 896000, tzinfo=tzlocal()),
    "FailureReason": "string",
    "IdentifiedLanguageScore": 10,
    "IdentifyLanguage": True,
    "JobExecutionSettings": {"AllowDeferredExecution": True, "DataAccessRoleArn": "arn:aws:iam::999999999999:role/TestTranscribe"},
    "LanguageCode": "string",
    "LanguageOptions": ["en-en", "en-ie"],
    "Media": {"MediaFileUri": f"https://s3-eu-west-1.amazonaws.com/{BUCKET_NAME}/{S3_AUDIO_FILE}"},
    "MediaFormat": "string",
    "MediaSampleRateHertz": 8000,
    "ModelSettings": {"LanguageModelName": "string"},
    "Settings": {
        "ChannelIdentification": True,
        "MaxAlternatives": 10,
        "MaxSpeakerLabels": 10,
        "ShowAlternatives": True,
        "ShowSpeakerLabels": True,
        "VocabularyFilterMethod": "string",
        "VocabularyFilterName": "string",
        "VocabularyName": "string",
    },
    "StartTime": datetime.datetime(2021, 7, 1, 14, 28, 6, 896000, tzinfo=tzlocal()),
    "Transcript": {"RedactedTranscriptFileUri": "string", "TranscriptFileUri": "string"},
    "TranscriptionJobName": "string",
    "TranscriptionJobStatus": "string",
}


class TranscribeLaunch:
    @contextmanager
    def ssm_setup(self, ssm_client):
        ssm_client.put_parameter(
            Name=f"/voice/{CLIENT_NAME}/cdr_type",
            Description="CDR Type",
            Value="ringcentral",
            Type="String",
        )

        ssm_client.put_parameter(
            Name=f"/voice/{CLIENT_NAME}/transcribe_type",
            Description="Audio Transcript Type",
            Value="speaker",
            Type="String",
        )
        yield

    def mock_s3_upload(self, local_filename, s3_key, s3_client):
        with open(local_filename, "rb") as f:
            s3_client.upload_fileobj(f, BUCKET_NAME, s3_key)

    @contextmanager
    def s3_setup(self, s3_client):
        bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": "eu-west-1"})

        s3_mock_upload_list = []

        audio_file = (
            S3_AUDIO_FILE,
            f"{BASE_DIR}/voice_tests/test_data/thetalake_ringcentral/2020-06-25.f0f5cba1-a457-4f44-edb8-12def04cd9e0.mp3",
        )

        s3_mock_upload_list.append(audio_file)

        cdr_file = (
            f"dev.todo.voice/2021-06-30/2021-06-30.meta.134499-8f0b076f-5424-e795-7305-3867eadb2a9e.json",
            f"{BASE_DIR}/voice_tests/test_data/thetalake_ringcentral/2020-06-25.meta.f0f5cba1-a457-4f44-edb8-12def04cd9e0.json",
        )

        s3_mock_upload_list.append(cdr_file)

        for file_pair in s3_mock_upload_list:
            self.mock_s3_upload(local_filename=file_pair[1], s3_key=file_pair[0], s3_client=s3_client)

        yield

    @patch.object(boto3, "client")
    def launch_lambda_handler(self, boto_client_patch, ssm_client, s3_client, test_lambda_context):
        stubbed_client = botocore.session.get_session().create_client("transcribe")
        stubber = Stubber(stubbed_client)
        stubber.add_response(
            "start_transcription_job", service_response={"TranscriptionJob": Transcription_Response}, expected_params={}
        )
        stubber.activate()
        boto_client_patch.return_value = stubbed_client

        with boto_client_patch:
            with self.ssm_setup(ssm_client):
                with self.s3_setup(s3_client):
                    lambda_event = s3_event(event_bucket=BUCKET_NAME, event_key=S3_AUDIO_FILE)
                    lambda_handler(lambda_event, test_lambda_context)
