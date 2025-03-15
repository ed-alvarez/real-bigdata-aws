import re
from logging import getLogger
from time import time
from typing import Dict

from boto3 import client
from botocore.exceptions import ClientError, ValidationError
from voice_settings import cdrType, transcribe_boto, transcribeType
from voice_src.create_transcription_job.voice_object import voiceObject
from voice_src.helpers.helper_dataclass import DynamoTranscriptionRecord

log = getLogger()


def clean_job_name(file: str) -> str:
    clean_file: str = re.sub("[^0-9a-zA-Z/._-]+", "", file)
    return clean_file


class transcribeVoice:
    def __init__(self, event, transcribe_client=None, ssm_client=None):
        self._event = event
        self._transcribe_client = transcribe_client or client("transcribe")
        self._ssm_client = ssm_client or client("ssm")

    def process_event(self):
        voice_object: voiceObject = voiceObject(lambda_event=self._event)
        voice_object.parseEvent()

        transcription_record: DynamoTranscriptionRecord = voice_object.TranscriptionRecord

        transcribe_object = transcribeAudioToText(transcription_record=transcription_record, transcribe_client=self._transcribe_client)
        transcribe_object.parse_audio()

        transcription_record.transcriptionJob = transcribe_object.transcriptionJob["TranscriptionJobName"]
        transcription_record.transcriptionStartTime = transcribe_object.transcriptionJob["StartTime"]
        transcription_record.generate_transcription_file_key()
        transcription_record.put_dynamo_transcription_job()


class transcribeAudioToText:
    """Take a VoiceObject, create an AWS transcription Job & return the TranscriptionJob parameters

    :param voiceObject: a VoiceObject with the data of the file to be processed
    :type voiceObject: voiceObject
    :return transcriptionJob: A dict with the transcription job details
    :rtype: Dict
    """

    def __init__(
        self, transcription_record: DynamoTranscriptionRecord, language_code: str = "", transcribe_client=None, ssm_client=None
    ) -> None:
        self._transcription_record: DynamoTranscriptionRecord = transcription_record
        self._transcribe_client = transcribe_client or client("transcribe")
        self._ssm_client = ssm_client or client("ssm")
        self._transcription_job: str
        self._language_code: str
        if language_code:
            self._language_code = self._check_language_code(language_code)
        else:
            self._language_code = None

    @property
    def transcriptionJob(self) -> Dict:
        return self._transcription_job

    @property
    def languageCode(self) -> str:
        return self._language_code

    def _get_transcribe_settings(self, client: str) -> Dict:
        log.debug(f"Getting parameter: /{client}/voice/transcribe_type")
        try:
            ssm_transcribe_type: str = self._ssm_client.get_parameter(Name=f"/{client}/voice/transcribe_type")["Parameter"]["Value"]
        except ValidationError or ClientError as ex:
            log.exception(ex)
            log.info(f"Parameter /{client}/voice/transcribe_type NOT found defaulting to {transcribeType.speaker.value}")
            ssm_transcribe_type = transcribeType.speaker.value
        # ssm_cdr_type = self._ssm_client.get_parameter(Name=f'/voice/{client}/cdr_type')['Parameter']['Value']

        # TRANSCRIBE_TYPE: transcribeType = transcribeType[ssm_transcribe_type]
        # CDR_TYPE : cdrType = cdrType[ssm_cdr_type]
        transcribe_settings: Dict = transcribe_boto[ssm_transcribe_type]
        return transcribe_settings

    def _check_language_code(self, value: str) -> str:
        """'
        One of ...
        'en-US'|'es-US'|'en-AU'|'fr-CA'|'en-GB'|'de-DE'|'pt-BR'|
        'fr-FR'|'it-IT'|'ko-KR'|'es-ES'|'en-IN'|'hi-IN'|'ar-SA'|
        'ru-RU'|'zh-CN'|'nl-NL'|'id-ID'|'ta-IN'|'fa-IR'|'en-IE'|
        'en-AB'|'en-WL'|'pt-PT'|'te-IN'|'tr-TR'|'de-CH'|'he-IL'|
        'ms-MY'|'ja-JP'|'ar-AE'
        """
        if value in [
            "en-US",
            "es-US",
            "en-AU",
            "fr-CA",
            "en-GB",
            "de-DE",
            "pt-BR",
            "fr-FR",
            "it-IT",
            "ko-KR",
            "es-ES",
            "en-IN",
            "hi-IN",
            "ar-SA",
            "ru-RU",
            "zh-CN",
            "nl-NL",
            "id-ID",
            "ta-IN",
            "fa-IR",
            "en-IE",
            "en-AB",
            "en-WL",
            "pt-PT",
            "te-IN",
            "tr-TR",
            "de-CH",
            "he-IL",
            "ms-MY",
            "ja-JP",
            "ar-AE",
        ]:
            return value
        else:
            return "en-GB"

    def _generate_timestamp(self) -> str:
        timestamp: str = str(time()).replace(".", "-")
        log.debug(f"timestamp : {timestamp}")
        return timestamp

    def _generate_job_name(self, client_name: str, file_name: str, time_stamp: str) -> str:
        job_name_raw: str = "-".join([client_name, file_name, time_stamp])
        job_name = clean_job_name(file=job_name_raw)
        log.debug(f"job_name : {job_name}")
        return job_name

    def _generate_job_output(self, file_directory: str, file_name: str) -> str:
        job_output: str = f"{str(file_directory)}/{file_name}.json"
        log.debug(f"job_output_key : {job_output}")
        return job_output

    def _generate_media_format(self, media_file_ext: str) -> str:
        media_format: str = media_file_ext.replace(".", "")
        log.debug(f"media_format : {media_format}")
        return media_format

    def _generate_job_uri(self, job_uri: str) -> Dict:
        job_uri = {"MediaFileUri": job_uri}
        log.debug(f"job_uri : {job_uri}")
        return job_uri

    def generate_transcribe_job(self, transcription_record: DynamoTranscriptionRecord, language_code: str) -> Dict:

        timestamp: str = self._generate_timestamp()

        job_name: str = self._generate_job_name(
            client_name=transcription_record.client, file_name=transcription_record.audioFileParts.file_stem, time_stamp=timestamp
        )

        job_output_key: str = self._generate_job_output(
            file_directory=transcription_record.audioFileParts.directory, file_name=job_name
        )

        job_uri: Dict = self._generate_job_uri(job_uri=transcription_record.audioFileURI)

        media_format: str = self._generate_media_format(media_file_ext=transcription_record.audioFileParts.file_ext)

        output_bucket: str = transcription_record.bucket
        log.debug(f"output_bucket : {output_bucket}")

        settings = self._get_transcribe_settings(client=transcription_record.client)
        log.debug(f"settings : {settings}")

        job_detail: Dict = {}
        job_detail["TranscriptionJobName"] = job_name
        job_detail["Media"] = job_uri
        job_detail["MediaFormat"] = media_format
        job_detail["OutputBucketName"] = output_bucket
        job_detail["OutputKey"] = job_output_key
        job_detail["Settings"] = settings

        if language_code:
            job_detail["LanguageCode"] = language_code
        else:
            job_detail["IdentifyLanguage"] = True

        log.debug(job_detail)

        return job_detail

    def parse_audio(self):
        job_detail: Dict = self.generate_transcribe_job(
            transcription_record=self._transcription_record, language_code=self._language_code
        )
        try:
            log.info("Start Transcription Job")
            response = self._transcribe_client.start_transcription_job(**job_detail)
        except Exception as ex:
            log.exception("Transcription Job error")
            raise Exception(ex)

        self._transcription_job = response["TranscriptionJob"]
        log.info("Transcription Job succeeded")
        log.debug(f"transcription_job : {self._transcription_job}")
        return
