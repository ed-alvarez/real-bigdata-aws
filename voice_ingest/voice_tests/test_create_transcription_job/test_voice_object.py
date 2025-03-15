from voice_src.create_transcription_job.voice_object import voiceObject
from voice_src.helpers.helper_dataclass import DynamoTranscriptionRecord
from voice_tests.test_data.events.s3_event import create_event as s3_event


class TestVoiceObject:
    def test_s3_event(self, ssm_voice_setup):
        with ssm_voice_setup:
            lambda_event = s3_event(
                event_bucket="ips.ips", event_key=f"todo.voice/2021-03-09/2021-03-09.13837a13-9049-70c6-8123-545eebc42abd.mp3"
            )
            voice_object = voiceObject(lambda_event=lambda_event)
            voice_object.parseEvent()
            dataclass_obj: DynamoTranscriptionRecord = voice_object.TranscriptionRecord

            assert dataclass_obj.client == "ips"
            assert (
                dataclass_obj.audioFileURI
                == "https://s3-eu-west-1.amazonaws.com/ips.ips/todo.voice/2021-03-09/2021-03-09.13837a13-9049-70c6-8123-545eebc42abd.mp3"
            )
            assert dataclass_obj.audioFileParts.file_ext == ".mp3"
            assert dataclass_obj.audioFileParts.file_stem == "2021-03-09.13837a13-9049-70c6-8123-545eebc42abd"

    def test_manual_event(self, ssm_voice_setup):
        with ssm_voice_setup:
            lambda_event = {"client": "ips", "key": "todo.voice/2021-03-09/2021-03-09.13837a13-9049-70c6-8123-545eebc42abd.mp3"}
            voice_object = voiceObject(lambda_event=lambda_event)
            voice_object.parseEvent()
            dataclass_obj: DynamoTranscriptionRecord = voice_object.TranscriptionRecord

            assert dataclass_obj.client == "ips"
            assert (
                dataclass_obj.audioFileURI
                == "https://s3-eu-west-1.amazonaws.com/ips.ips/todo.voice/2021-03-09/2021-03-09.13837a13-9049-70c6-8123-545eebc42abd.mp3"
            )
            assert dataclass_obj.audioFileParts.file_ext == ".mp3"
            assert dataclass_obj.audioFileParts.file_stem == "2021-03-09.13837a13-9049-70c6-8123-545eebc42abd"
