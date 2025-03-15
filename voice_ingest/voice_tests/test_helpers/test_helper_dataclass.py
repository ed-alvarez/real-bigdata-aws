from contextlib import contextmanager
from datetime import datetime

from dateutil.tz import tzlocal
from voice_src.helpers.helper_dataclass import DynamoTranscriptionRecord


class TestFunction:
    def test_instatiate_blank_DynamoTranscriptionRecord(self, ssm_voice_setup):
        with ssm_voice_setup:
            object: DynamoTranscriptionRecord = DynamoTranscriptionRecord()
            assert object.client == ""

    def test_populate_DynamoTranscriptionRecord(self, ssm_voice_setup):
        with ssm_voice_setup:
            start_time = datetime(2020, 5, 26, 14, 56, 22, 88000, tzinfo=tzlocal())
            object: DynamoTranscriptionRecord = DynamoTranscriptionRecord(
                client="ips", audioFileKey="todo.voice/2021-03-09/2021-03-09.AudioFileKey.mp3"
            )
            object.generate_data()
            object.generate_cdr_file_key()
            object.transcriptionJob = "transcriptionjob"
            object.transcriptionStartTime = start_time
            object.generate_transcription_file_key()

            assert (
                object.audioFileURI == "https://s3-eu-west-1.amazonaws.com/ips.ips/todo.voice/2021-03-09/2021-03-09.AudioFileKey.mp3"
            )

    def test_generate_transaction_in_DynamoTranscriptionRecord(self, ssm_voice_setup):
        with ssm_voice_setup:
            start_time = datetime(2020, 5, 26, 14, 56, 22, 88000, tzinfo=tzlocal())
            object: DynamoTranscriptionRecord = DynamoTranscriptionRecord(
                client="ips", audioFileKey="dev.todo.voice/2021-03-09/2021-03-09.AudioFileKey.mp3"
            )
            object.generate_data()
            object.generate_cdr_file_key()

            object.transcriptionJob = "transcriptionjob"
            object.transcriptionStartTime = start_time
            object.generate_transcription_file_key()

            assert object.audioFileParts.file_ext == ".mp3"

    def test_save_DynamoTranscriptionRecord_to_dyanmo(self, ssm_voice_setup, dynamo_db_voice_setup):
        with ssm_voice_setup as a, dynamo_db_voice_setup as b:
            start_time = datetime(2020, 5, 26, 14, 56, 22, 88000, tzinfo=tzlocal())
            object: DynamoTranscriptionRecord = DynamoTranscriptionRecord(
                client="ips", audioFileKey="todo.voice/2021-03-09/2021-03-09.AudioFileKey.mp3"
            )
            object.generate_data()
            object.generate_cdr_file_key()

            object.transcriptionJob = "transcriptionjob"
            object.transcriptionStartTime = start_time
            object.generate_transcription_file_key()
            response = object.put_dynamo_transcription_job()
            assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    def test_retrieve_dynamo_to_DynamoTranscriptionRecord(self, ssm_voice_setup, dynamo_db_voice_setup):
        with ssm_voice_setup:
            with dynamo_db_voice_setup:
                start_time = datetime(2020, 5, 26, 14, 56, 22, 88000, tzinfo=tzlocal())
                object: DynamoTranscriptionRecord = DynamoTranscriptionRecord(
                    client="ips", audioFileKey="todo.voice/2021-03-09/2021-03-09.AudioFileKey.mp3"
                )
                object.generate_data()
                object.generate_cdr_file_key()

                object.transcriptionJob = "transcriptionjob"
                object.transcriptionStartTime = start_time
                object.generate_transcription_file_key()
                response = object.put_dynamo_transcription_job()

                new_obj: DynamoTranscriptionRecord = DynamoTranscriptionRecord(
                    transcriptionJob="transcriptionjob", transcriptionFileKey="todo.voice/2021-03-09/transcriptionjob.json"
                ).get_dynamo_transcription_job()

                assert new_obj.bucket == "ips.ips"
