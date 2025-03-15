from logging import getLogger
from typing import Dict, Optional
from urllib.parse import unquote_plus

from voice_settings import eventType
from voice_src.helpers.helper_dataclass import DynamoTranscriptionRecord

log = getLogger()


class voiceObject:
    """
    An object to parse an s3Bucket or manual event and hold all the data around Transcription Jobs

    """

    def __init__(self, lambda_event: Dict):
        self._lambda_event: Dict[str, any] = lambda_event
        self._transcriptionRecord: Optional[DynamoTranscriptionRecord] = None

    @property
    def TranscriptionRecord(self) -> DynamoTranscriptionRecord:
        return self._transcriptionRecord

    def _return_client_from_bucket(self, bucket) -> str:
        client_decode: str = bucket.rsplit(".", 1)[0]
        if client_decode.split(".")[0] in ["todo", "stash", "archive"]:
            return client_decode.split(".")[1]
        else:
            return client_decode

    def _populate_from_s3_action(self, lambda_event: Dict) -> DynamoTranscriptionRecord:
        client: str = self._return_client_from_bucket(lambda_event["Records"][0]["s3"]["bucket"]["name"])
        key: str = unquote_plus(self._lambda_event["Records"][0]["s3"]["object"]["key"])

        transcription_record: DynamoTranscriptionRecord = DynamoTranscriptionRecord(client=client, audioFileKey=key)
        transcription_record.generate_data()
        transcription_record.generate_cdr_file_key()
        return transcription_record

    def _populate_from_manual_event(self, lambda_event: Dict) -> DynamoTranscriptionRecord:
        client: str = lambda_event["client"]
        key: str = unquote_plus(lambda_event["key"])
        transcription_record: DynamoTranscriptionRecord = DynamoTranscriptionRecord(client=client, audioFileKey=key)
        transcription_record.generate_data()
        transcription_record.generate_cdr_file_key()
        return transcription_record

    def parseEvent(self) -> None:
        result: Optional[DynamoTranscriptionRecord] = None
        if "Records" not in self._lambda_event:
            result = self._populate_from_manual_event(self._lambda_event)
        elif eventType.S3.value in self._lambda_event["Records"][0]:
            result = self._populate_from_s3_action(self._lambda_event)
        self._transcriptionRecord = result
