import json
import pathlib
from ast import literal_eval
from collections import OrderedDict
from datetime import datetime
from logging import getLogger
from typing import Dict, List, Optional, Tuple

from boto3 import client
from lxml import etree as ET
from voice_settings import MSG_TYPE, cdrType, processingStage, transcribeType
from voice_src.helpers.helper_dataclass import DynamoTranscriptionRecord
from voice_src.helpers.helper_s3 import s3Helper
from voice_src.process_transcript_job.cdr_parsers.base_parser import CdrParser
from voice_src.process_transcript_job.cdr_parsers.freeswitch import Freeswitch
from voice_src.process_transcript_job.cdr_parsers.red_box import RedBox
from voice_src.process_transcript_job.cdr_parsers.ring_central import RingCentral
from voice_src.process_transcript_job.cdr_parsers.verba import Verba
from voice_src.process_transcript_job.elastic_search.es_voice_index_v1 import (
    VOICE,
    Fingerprint_Meta,
    Schema,
)
from voice_src.process_transcript_job.elastic_search.helper_upload_to_es import (
    UploadToElasticsearch,
)
from voice_src.process_transcript_job.files_object import transcriptionFile
from voice_src.process_transcript_job.transcript_parsers.route_transcript import (
    RouteTranscript,
)

log = getLogger()


class ProcessTranscript:
    @staticmethod
    def etree_to_dict(root, include_root_tag=False):
        root = root
        result = OrderedDict()
        if len(root) > 1 and len({child.tag for child in root}) == 1:
            result[next(iter(root)).tag] = [ProcessTranscript.etree_to_dict(child) for child in root]
        else:
            for child in root:
                result[child.tag] = ProcessTranscript.etree_to_dict(child) if len(list(child)) > 0 else (child.text or "")
        result.update(("@" + k, v) for k, v in root.attrib.items())
        return {root.tag: result} if include_root_tag else result

    def __init__(self, event: Dict, context: Dict, ssm_client=None):
        self._event: Dict = event
        self._job_name: str = self._event["detail"]["TranscriptionJobName"]

        self._context: Dict = context
        self._transcript_record: Optional[DynamoTranscriptionRecord] = None
        self._fingerprint_metadata: Fingerprint_Meta = Fingerprint_Meta()

        self._transcribed_data = None
        self._cdr_data = None
        self._job_info: transcriptionFile = transcriptionFile()
        self._s3_helper: s3Helper = s3Helper()

        self._es_voice_record: VOICE = VOICE()
        self._es_upload: UploadToElasticsearch = None
        self._ssm_client = ssm_client or client("ssm")

    def _set_key_to_new_processing_stage(self, key: str, current_stage: processingStage, new_stage: processingStage) -> str:
        new_key: str = key.replace(current_stage.value, new_stage.value)
        return new_key

    def _populate_job_info_object(self, job_name: str) -> DynamoTranscriptionRecord:
        transcription_record: DynamoTranscriptionRecord = DynamoTranscriptionRecord(
            transcriptionJob=job_name
        ).get_dynamo_transcription_job()
        return transcription_record

    def _get_s3_transcript_key(self):
        return {"Key": self._transcript_record.transcriptionFileKey, "Bucket": self._transcript_record.bucket}

    def _get_s3_cdr_key(self, replace_from: str = "", replace_to: str = "") -> Dict:
        # this is a hack and would be better to pass the correct file name
        key_raw: str = self._transcript_record.cdrFileKey
        key_clean: str = key_raw
        if replace_from:
            log.debug(f"{key_clean} replace {replace_from} with {replace_to}")
            key_clean = key_raw.replace(replace_from, replace_to)
        log.debug(f"Key = {key_clean}")
        return {"Key": key_clean, "Bucket": self._transcript_record.bucket}

    def transcribe_file(self, key: Dict, transcribe_type: transcribeType) -> VOICE:
        transcript_file = self._s3_helper.get_file_body_from_s3(key)
        parse_json = RouteTranscript()
        parse_json.rawJSON = transcript_file
        parse_json.transcribeType = transcribe_type
        try:
            parse_json.parse_transcribe_file()
        except Exception as ex:
            log.exception(ex)

        return parse_json.esVoice

    def _file_extension_of_cdr(self, key: dict) -> str:
        file: str = key["Key"]
        file_extension: str = pathlib.Path(file).suffix
        return file_extension.lower()

    def _decode_file_content_to_dict(self, content: str, extension: str) -> Dict:
        cdr_dict: Dict = {}
        if "json" in extension:
            # cdr_dict = literal_eval(content)
            cdr_dict = json.loads(content)
            log.debug(f"cdr JSON loaded to dict : {cdr_dict}")
        elif "xml" in extension:
            xml = content.encode("utf-8")
            parser = ET.XMLParser(ns_clean=True, recover=True, encoding="utf-8")
            xml_data = ET.fromstring(xml, parser=parser)
            cdr_dict: Dict = self.etree_to_dict(xml_data)
            log.debug(f"cdr XML loaded to dict : {cdr_dict}")
        else:
            log.error(f"cannot load CDR in {extension} type files")
            raise ValueError
        return cdr_dict

    def _load_cdr_from_s3(self, key: Dict) -> Dict:
        log.debug(f"loading cdr file {key}")

        cdr_file_content: str = ""

        try:
            cdr_file_content: str = self._s3_helper.get_file_body_from_s3(key)
        except Exception as ex:
            log.warning(f"{key} not found")
            log.warning(ex)
            pass

        if not cdr_file_content:
            # this is a hack and would be better to pass the correct file name
            log.debug("replace .json with .xml and try again")
            key = self._get_s3_cdr_key(replace_from=".json", replace_to=".xml")
            try:
                cdr_file_content: str = self._s3_helper.get_file_body_from_s3(key)
            except Exception as ex:
                log.warning(f"{key} also not found")
                log.warning(ex)
                raise ex
        try:
            cdr_file_extension: str = self._file_extension_of_cdr(key=key)
        except Exception as ex:
            log.warning(f"file extension of {key} not found")
            log.warning(ex)
            raise ex

        cdr_dict: Dict = self._decode_file_content_to_dict(content=cdr_file_content, extension=cdr_file_extension)
        return cdr_dict

    def _parse_cdr(self, cdr_dict: Dict, cdr_type: cdrType) -> VOICE:

        log.debug(f"Loading parser for {cdr_type.value}")
        parse_cdr: CdrParser = CdrParser.get(cdr_type.value)(cdr_dict=cdr_dict)
        try:
            parse_cdr.process_cdr()
        except Exception as ex:
            log.exception(ex)
            raise ex

        return parse_cdr.esVoice

    def _populate_fingerprint_meta(self, transcript_record: DynamoTranscriptionRecord) -> Fingerprint_Meta:
        log.debug("Update fingerprint meta with date")
        fingerprint_meta: Fingerprint_Meta = Fingerprint_Meta()

        fingerprint_meta.time = self._es_voice_record.date
        audio_key_name: str = self._set_key_to_new_processing_stage(
            key=self._transcript_record.audioFileKey, current_stage=processingStage.todo, new_stage=processingStage.processed
        )

        transcript_key_name: str = self._set_key_to_new_processing_stage(
            key=transcript_record.transcriptionFileKey, current_stage=processingStage.todo, new_stage=processingStage.processed
        )

        cdr_key_name: str = self._set_key_to_new_processing_stage(
            key=transcript_record.cdrFileKey, current_stage=processingStage.todo, new_stage=processingStage.processed
        )

        fingerprint_meta.client = transcript_record.client
        fingerprint_meta.bucket = transcript_record.bucket
        fingerprint_meta.key = audio_key_name
        fingerprint_meta.type = MSG_TYPE
        fingerprint_meta.processed_time = datetime.now()
        fingerprint_meta.aws_lambda_id = self._context.aws_request_id

        fingerprint_meta.key_audio = audio_key_name
        fingerprint_meta.key_transcript = transcript_key_name
        fingerprint_meta.key_cdr = cdr_key_name
        fingerprint_meta.schema = Schema.version

        # TODO
        # self._fingerprint_metadata.msgTime = date
        # self._fingerprint_metadata.keyNameAudio = self._event_obj.path.processedKey
        # self._fingerprint_metadata.subType = [system of Audio Processed]
        # self._fingerprint_metadata.subType = [system of Audio Processed]
        return fingerprint_meta

    def _populate_es_voice_record(
        self, transcribed_data: VOICE, cdr_data: VOICE, transcript_record: DynamoTranscriptionRecord
    ) -> VOICE:

        es_voice: VOICE = VOICE()

        es_voice.body_detail = transcribed_data.body_detail
        es_voice.body = transcribed_data.body

        es_voice.from_ = cdr_data.from_
        es_voice.to = cdr_data.to
        es_voice.date = cdr_data.date

        fingerprint_meta: Fingerprint_Meta = self._populate_fingerprint_meta(transcript_record=transcript_record)
        fingerprint_meta.time = cdr_data.date
        es_voice.fingerprint = fingerprint_meta

        return es_voice

    def _upload_transcript_to_es(self, es_id: str, es_voice: VOICE) -> None:
        # Update with Fingerprint metadata
        log.debug("add fingerprint metadata to es voice record")
        self._es_upload = UploadToElasticsearch()
        self._es_upload.voiceDict = es_voice
        self._es_upload.esId = es_id
        self._es_upload.do_upload()

    def _file_move_to_processed_and_copy_to_archive(self, key: str, bucket: str) -> None:
        self._s3_helper.copy_object(file_key=key, bucket=bucket, from_root=processingStage.todo, to_root=processingStage.archived)

        self._s3_helper.move_object_between_roots(
            file_key=key, bucket=bucket, from_root=processingStage.todo, to_root=processingStage.processed
        )
        return

    def _is_valid_transcript(self, event: Dict) -> bool:
        is_valid_transcript: bool = False
        job_status: str = event["detail"].get("TranscriptionJobStatus")
        if job_status == "COMPLETED":
            is_valid_transcript = True
        else:
            failure_reason: str = event["detail"].get("FailureReason", "Unknown Reason")
            log.error(failure_reason)
        return is_valid_transcript

    def _move_files(self, transcript_record: DynamoTranscriptionRecord, is_valid_transcript: bool) -> None:
        file_list: List = []
        file_list.append(transcript_record.audioFileKey)
        if is_valid_transcript:
            file_list.append(transcript_record.cdrFileKey)
            file_list.append(transcript_record.transcriptionFileKey)

        for file in file_list:
            self._file_move_to_processed_and_copy_to_archive(key=file, bucket=transcript_record.bucket)
        return

    def _get_transcribe_settings(self, client: str) -> Tuple:
        ssm_transcribe_type: str = self._ssm_client.get_parameter(Name=f"/{client}/voice/transcribe_type")["Parameter"]["Value"]
        ssm_cdr_type = self._ssm_client.get_parameter(Name=f"/{client}/voice/cdr_type")["Parameter"]["Value"]

        transcribe_type: transcribeType = transcribeType[ssm_transcribe_type]
        cdr_type: cdrType = cdrType[ssm_cdr_type]
        return transcribe_type, cdr_type

    def process_transcript(self):
        # Check status of event
        #
        self._transcript_record: DynamoTranscriptionRecord = self._populate_job_info_object(self._job_name)

        is_valid_transcript: bool = self._is_valid_transcript(event=self._event)

        if is_valid_transcript:
            transcript_type, cdr_type = self._get_transcribe_settings(client=self._transcript_record.client)

            self._transcribed_data: VOICE = self.transcribe_file(key=self._get_s3_transcript_key(), transcribe_type=transcript_type)

            cdr_dict: Dict = self._load_cdr_from_s3(key=self._get_s3_cdr_key())
            self._cdr_data: VOICE = self._parse_cdr(cdr_dict=cdr_dict, cdr_type=cdr_type)

            es_voice: VOICE = self._populate_es_voice_record(
                transcribed_data=self._transcribed_data, cdr_data=self._cdr_data, transcript_record=self._transcript_record
            )

            self._upload_transcript_to_es(es_id=self._job_name, es_voice=es_voice)

        self._move_files(transcript_record=self._transcript_record, is_valid_transcript=is_valid_transcript)
        return True
