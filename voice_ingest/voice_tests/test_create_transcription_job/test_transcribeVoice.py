import datetime

import pytest
from dateutil.tz import tzlocal
from voice_src.create_transcription_job.transcribe import (
    clean_job_name,
    transcribeVoice,
)
from voice_src.create_transcription_job.voice_object import voiceObject

CLIENT_NAME = "testing"
BUCKET_NAME = f"{CLIENT_NAME}.ips"
S3_AUDIO_FILE = "dev.todo.voice/2021-06-30/2021-06-30.134499-8f0b076f-5424-e795-7305-3867eadb2a9e.mp3"
lambda_event = {"client": CLIENT_NAME, "key": S3_AUDIO_FILE}

Transcription_Response = {
    "TranscriptionJob": {
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
}


@pytest.fixture
def generate_voice_object():

    voice_object = voiceObject(lambda_event=lambda_event)
    voice_object.parseEvent()
    yield voice_object


class TestFunctions:
    class stub_transcribe:
        def start_transcription_job(self, **kwargs):
            return Transcription_Response

    def test_transcribe_voice(self, test_lambda_context, generate_voice_object, ssm_voice_setup, dynamo_db_voice_setup):
        stub_transcribe_client = self.stub_transcribe()
        with ssm_voice_setup:
            with dynamo_db_voice_setup:
                obj_transcribe_voice = transcribeVoice(event=lambda_event, transcribe_client=stub_transcribe_client)
                obj_transcribe_voice.process_event()

    def test_clean_job_name(self):
        job_name = "dev.todo.voice/dev-saxo-8912351--009711056757#_2022-01-13_14-02-1643130977-2065554.json"
        result = clean_job_name(job_name)
        assert result == "dev.todo.voice/dev-saxo-8912351--009711056757_2022-01-13_14-02-1643130977-2065554.json"
