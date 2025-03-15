import logging
import sys
from pathlib import Path

import dataclass_wizard

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))  # for any host run-time
sys.path.append(str(tenant_directory))

from zoom_settings import INGEST_SOURCE, STAGE, BucketStage, FileExtension, zoomType
from zoom_shared.api_client import ZoomAPI
from zoom_shared.zoom_dataclasses import (
    Recording,
    Transcript,
    ZoomDTO,
    ZoomFilesTracker,
)
from zoom_shared.zoom_utils import lamda_write_to_s3

from shared.shared_src.s3.s3_helper import S3Helper
from shared.shared_src.utils import webvtt_parse_content

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MediaController:
    def __init__(
        self,
        zoom_file_tracker: ZoomFilesTracker,
        api_client: ZoomAPI = None,
        s3_client: S3Helper = None,
    ):
        self.step_tracker: ZoomFilesTracker = zoom_file_tracker
        self.customer: str = self.step_tracker.customer

        if (api_client and s3_client) is None:
            self._init_clients()
        else:
            self.api_client: ZoomAPI = api_client
            self.s3_client: S3Helper = s3_client

    def enhance_blob_call(self, raw_todo_call_uri: str) -> None:
        index_at_list: int = self.step_tracker.calls.index(raw_todo_call_uri)
        raw_todo_call_uri: str = self.step_tracker.calls.pop(index_at_list)

        blob: bytes = self.s3_client.get_file_content(raw_todo_call_uri)
        blob: dict = self.s3_client.to_json(blob)

        # Call blob before enhancing
        call_todo_blob: ZoomDTO = dataclass_wizard.fromdict(ZoomDTO, blob)
        if call_todo_blob.cdr.source.source_type == zoomType.call.value:
            enhanced_call_blob: ZoomDTO = self._update_enhance_audio_call_blob(
                call_todo_blob
            )
            self.update_todo_bucket(enhanced_call_blob, raw_todo_call_uri)

    def _update_enhance_audio_call_blob(self, call_blob: ZoomDTO) -> ZoomDTO:
        recording: Recording = call_blob.recording
        source_type: str = recording.source.source_type
        source_id: str = str(recording.source.source_id)

        download_url: str = recording.download_url
        audio_file: bytes = self.api_client.download_endpoint(
            download_url, download_media=True
        )
        # Downloading Audio MP3 Recording

        retries = 0
        while len(audio_file) < 1024:  # 1,024 KB
            logger.warn(
                f"Zoom audio download may be corrupted. Total Bytes are {len(audio_file)}"
            )
            retries = retries + 1
            if retries == 3:
                break

        # Save media at S3
        audio_file_uri: str = lamda_write_to_s3(
            obj=audio_file,
            prefix_stage=f"audio_file_{source_type}_{source_id}",
            ingest_source=INGEST_SOURCE,
            bucket_stage=BucketStage.PROCESS.value,
            customer=self.step_tracker.customer,
            extension=FileExtension.MP3.value,
            date_from_event=call_blob.cdr.date_of_action.split(" ")[0],
        )
        # Play URL at Zoom need to append JWT to be listened
        call_blob.recording.play_url = call_blob.recording.play_url.split("&jwt=")[0]
        call_blob.recording.download_url = audio_file_uri
        return call_blob

    def enhance_blob_meet(self, raw_todo_meet_uri: str) -> None:
        index_at_list: int = self.step_tracker.meets.index(raw_todo_meet_uri)
        raw_todo_meet_uri: str = self.step_tracker.meets.pop(index_at_list)

        blob: bytes = self.s3_client.get_file_content(raw_todo_meet_uri)
        blob: dict = self.s3_client.to_json(blob)
        self._add_empty_destination(blob)

        # Meet blob before enhancing
        meet_todo_blob: ZoomDTO = dataclass_wizard.fromdict(ZoomDTO, blob)
        if meet_todo_blob.cdr.source.source_type == zoomType.meet.value:
            enhanced_meet_blob: ZoomDTO = (
                self._update_enhance_transcript_audio_meet_blob(meet_todo_blob)
            )
            self.update_todo_bucket(enhanced_meet_blob, raw_todo_meet_uri)

    def _update_enhance_transcript_audio_meet_blob(self, meet_blob: ZoomDTO) -> ZoomDTO:
        transcript: Transcript = meet_blob.transcript

        # Enhance Adding/Downloading Transcript
        if transcript.content != {}:
            # if there is available transcript download
            logger.debug(f"Transcript recording at {transcript.content}")
            transcript: bytes = self.api_client.download_endpoint(
                transcript.content, download_media=True
            )
            transcript: str = transcript.decode("utf-8")
            logger.debug(f"Transcript success here: {transcript}")
            try:  # & parse it
                transcript_content: dict = webvtt_parse_content(transcript)
                total_phrases = transcript_content["content"]
                logger.info(f"VTT phrases enhanced {len(total_phrases)}!")

                meet_blob.transcript.content = transcript_content
            except KeyError:
                logger.info("Error at transforming parse VTT transcript for meeting!")

        # Downloading Audio M4A Recording
        recording: Recording = meet_blob.recording
        source_type: str = recording.source.source_type
        source_id: str = str(recording.source.source_id).replace("/", "$")

        download_url: str = recording.download_url
        audio_file: bytes = self.api_client.download_endpoint(
            download_url, download_media=True
        )

        # Save media at S3
        audio_file_uri: str = lamda_write_to_s3(
            obj=audio_file,
            prefix_stage=f"audio_file_{source_type}_{source_id}",
            ingest_source=INGEST_SOURCE,
            bucket_stage=BucketStage.PROCESS.value,
            customer=self.step_tracker.customer,
            extension=FileExtension.M4A.value,
            date_from_event=meet_blob.cdr.date_of_action.split(" ")[0],
        )
        # Play URL at Zoom need to append JWT to be listened
        meet_blob.recording.play_url = meet_blob.recording.play_url.split("&jwt=")[0]
        meet_blob.recording.download_url = audio_file_uri
        return meet_blob

    def update_todo_bucket(self, updated_blob: ZoomDTO, todo_blob_uri: str):
        source_type: str = updated_blob.cdr.source.source_type

        updated_todo_uri: str = lamda_write_to_s3(
            obj=updated_blob,
            prefix_stage="ready",
            ingest_source=INGEST_SOURCE,
            bucket_stage=BucketStage.TODO.value,
            customer=self.step_tracker.customer,
            extension=FileExtension.JSON.value,
            date_from_event=updated_blob.cdr.date_of_action.split(" ")[0],
        )

        if source_type == zoomType.call.value:
            self.step_tracker.calls.append(updated_todo_uri)

        if source_type == zoomType.meet.value:
            self.step_tracker.meets.append(updated_todo_uri)

        if "prod" in STAGE:
            self.s3_client.s3_client.delete_object(
                Bucket=self.s3_client._bucket_name, Key=todo_blob_uri
            )

    def _init_clients(self):
        self.s3_client: S3Helper = S3Helper(
            client_name=self.step_tracker.customer,
            ingest_type=INGEST_SOURCE,
        )

        self.api_client = ZoomAPI(
            customer_name=self.step_tracker.customer,
            start_date=self.step_tracker.start_date,
            end_date=self.step_tracker.end_date,
        )

    def _add_empty_destination(self, blob):  # meetings only have participants
        no_destination_persona_details: dict = {
            "persona_id": "Unknown",
            "persona_first_name": "Unknown",
            "persona_second_name": "Unknown",
            "persona_number": "Unknown",
            "persona_email": "Unknown",
            "persona_department": "Unknown",
        }  # hence, adding empty destination
        blob["cdr"]["destination_to"] = no_destination_persona_details
        return blob
