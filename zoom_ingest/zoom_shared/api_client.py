import logging
import sys
import urllib.parse as encoder
from pathlib import Path
from typing import Any, Optional, Tuple, Union

import requests
from requests.adapters import HTTPAdapter, Retry

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))


from zoom_settings import *
from zoom_shared.zoom_dataclasses import CDR, Recording, Transcript, ZoomDTO
from zoom_shared.zoom_utils import (
    _empty_transcript,
    error_handler,
    generate_cdr_call,
    generate_cdr_meet,
    generate_recording_call,
    generate_recording_meet,
    generate_transcript_call,
    generate_transcript_meet,
    is_transcript_audio_recordings,
)

from shared.shared_src.auth.oauth2 import OAuth2
from shared.shared_src.tenant.base_tenant import Tenant

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE_URL = "https://api.zoom.us/v2"
Response = requests.models.Response


class ZoomAPI(OAuth2):
    _api = "zoom"

    def __init__(
        self, customer_name: str = "", start_date: str = "", end_date: str = ""
    ):
        logger.debug(f"Init Zoom API with {customer_name}| {start_date} | {end_date}")
        super().__init__(customer_name=customer_name)
        self.user_ids: dict = []
        self.users_info: list = []
        self.call_logs: list = []
        self.call_logs_ids: list = []
        self.meetings_with_recordings: list = []
        self.meet_ids: list = []
        self.recording_ids: list = []
        self.phone_transcripts: list = []
        self.start_date, self.end_date = Tenant.date_ranges(
            start_date=start_date,
            end_date=end_date,
        )

    def make_request(
        self,
        end_point: str,
        method: str = "GET",
        params: str = "",
        headers: dict = {},
        body: dict = {},
        download_media: bool = False,
    ) -> dict:
        data: dict = {}

        if not body:
            body = {}

        self._request_token()
        base_url: str = BASE_URL if not download_media else ""
        request_kwargs: dict = {
            "headers": self.get_headers(),
            "params": params,
            "body": body,
        }
        logger.info(f" HTTP {method}/ {base_url}{end_point}")

        full_url: str = f"{base_url}{end_point}{params}"

        if headers is not None:
            for key, value in headers.items():
                request_kwargs["headers"][key] = value

        logger.debug(f" HTTP Request {method}/ {full_url}")
        # logger.debug(f" Request Payload: {json.dumps(request_kwargs)}")

        session = requests.Session()
        retry = Retry(connect=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        response: Response = session.request(
            method=method,
            url=full_url,
            headers=request_kwargs["headers"],
            params=request_kwargs["params"],
            data=request_kwargs["body"],
        )

        logger.debug(f" HTTP Response {response}")

        try:
            if response.status_code >= 200 and response.status_code <= 300:
                data: Any = response.content if download_media else response.json()
                if not download_media:
                    logger.debug(f" Endpoint Response {data}")
            else:
                zoom_api_misfire: str = (
                    f"{method}/ {full_url} {response.status_code} | {response.json()} "
                )
                logger.warning(
                    zoom_api_misfire
                )  # Recording file not found or Invalid Account token

        except Exception as error:
            logger.error(f"Error at request {error}")

        return data

    #################################
    #   END POINTS
    #   INVOKES
    #################################

    def user_detail(self, user_id: str) -> dict:
        """
        https://marketplace.zoom.us/docs/api-reference/zoom-api/methods/#operation/user
        """
        return self.make_request(end_point=USER.format(user_id=user_id))

    def call_log_detail(self, call_log_id: str) -> dict:
        """
        https://marketplace.zoom.us/docs/api-reference/phone/methods/#operation/getCallLogDetails
        """
        return self.make_request(
            end_point=PHONE_CALL_LOG_DETAIL.format(call_log_id=call_log_id)
        )

    def download_endpoint(
        self,
        download_url: str,
        token: str = "",
        download_media: bool = False,
    ) -> Union[bytes, dict]:
        """
        Download conference cloud recorded file
        """
        file: Optional[bytes] = None
        try:
            if not token:
                self.get_headers()
                params: str = f"?access_token={self.token}"
            else:
                params: str = f"?access_token={token}"
            file: bytes = self.make_request(
                end_point=f"{download_url}{params}",
                download_media=download_media,
            )
        except ConnectionError as error:
            logger.error(f"call_blob.recording.play_url {error}")
        return file

    def list_users(self) -> Tuple:
        """
        Request zoom users list and return email with id.
        https://marketplace.zoom.us/docs/api-reference/zoom-api/methods/#operation/users
        :return: {
            'john@due.com': 1,
            'dummy@mail.com': 2
        }
        """
        user_list: dict = {}
        user_ids: dict = {}
        response: dict = {}

        try:
            response: dict = self.make_request(end_point=USERS)
            user_list: list = response["users"]
            user_ids: dict = {user["email"]: user["id"] for user in response["users"]}
            is_there_pagination: str = response["next_page_token"]

            while len(is_there_pagination) != 0:
                next_page: str = f"?next_page_token={is_there_pagination}"
                response: dict = self.make_request(end_point=USERS, params=next_page)

                user_list_temp: list = response["users"]
                user_list = dict(user_list, **user_list_temp)

                user_ids_temp: dict = {
                    user["email"]: user["id"] for user in response["users"]
                }
                user_ids = dict(user_list, **user_ids_temp)

                is_there_pagination: str = response["next_page_token"]

        except KeyError:
            logger.error("Error retrieving the users from account")

        return user_list, user_ids

    def list_calls_logs(self) -> dict:
        """
        Request call logs.
        https://marketplace.zoom.us/docs/api-reference/phone/methods/#operation/accountCallLogs
        :return: [
            # Referred to call_logs.json file under temp_utils folder
        ]
        """
        call_logs: list = []

        date_range_param: str = f"?from={self.start_date}&to={self.end_date}"
        response: dict = self.make_request(
            end_point=PHONE_CALL_LOGS, params=date_range_param
        )

        try:
            call_logs: list = response["call_logs"]
            call_logs: list = [
                call_log for call_log in call_logs if call_log.get("recording_id", {})
            ]
            is_there_pagination: str = response["next_page_token"]
            while is_there_pagination != "":
                next_page: str = (
                    f"{date_range_param}&next_page_token={is_there_pagination}"
                )
                response: dict = self.make_request(
                    end_point=PHONE_CALL_LOGS, params=next_page
                )
                is_there_pagination: str = response["next_page_token"]
                response: list = response["call_logs"]
                response: list = [
                    call_log
                    for call_log in response
                    if call_log.get("recording_id", {})
                ]
                call_logs.extend(response)

        except KeyError:
            logger.error("No call logs found!")

        return call_logs

    def list_meetings_recordings(self, user_id: str) -> dict:
        """
        Request meetings recordings under user.
        https://marketplace.zoom.us/docs/api-reference/zoom-api/methods/#operation/recordingsList
        :param user_id: zoom_user_id
        :return: {
                "from": "2022-01-01",
                "to": "2022-04-01",
                "next_page_token": "Tva2CuIdTgsv8wAnhyAdU3m06Y2HuLQtlh3",
                "page_count": 1,
                "page_size": 30,
                "total_records": 1,
                "meetings": [
                    # Referred to meeting_recording.json file under temp_utils folder
                ]
            }
        """
        next_page: str = ""
        response: dict = {}
        meeting_recordings: dict = {}
        date_range_param: str = f"?from={self.start_date}&to={self.end_date}"

        try:
            response: dict = self.make_request(
                end_point=RECORDINGS.format(user_id=user_id),
                params=date_range_param,
            )
            meeting_recordings = response["meetings"]
        except Exception as error:
            logger.error(f"User doesn't have meeting recordings {error}")

        try:
            is_there_pagination: str = response["next_page_token"]
            while is_there_pagination != "":
                next_page: str = f"?next_page_token={is_there_pagination}"
                response: dict = self.make_request(
                    end_point=RECORDINGS.format(user_id=user_id),
                    params=next_page,
                )

                meeting_recordings_temp: list = response["meetings"]
                meeting_recordings: dict = dict(
                    meeting_recordings, **meeting_recordings_temp
                )
                is_there_pagination: str = response["next_page_token"]

        except KeyError:
            logger.error("Error at reading pagination for meeting recordings!")

        return meeting_recordings

    def past_meeting_participants(self, meeting_id: Union[str, int]) -> dict:
        """
        Use this API to get participants from a past meeting
        https://marketplace.zoom.us/docs/api-reference/zoom-api/methods/#operation/pastMeetingParticipants
        """
        return self.make_request(
            end_point=MEETING_PARTICIPANTS.format(meeting_id=meeting_id),
        )

    def meeting_detail(self, meeting_id: int) -> dict:
        """
        https://marketplace.zoom.us/docs/api-reference/zoom-api/methods/#operation/meeting
        """
        return self.make_request(end_point=MEETING_DETAIL.format(meeting_id=meeting_id))

    def call_log_detail(self, call_log_id: str) -> dict:
        """
        https://marketplace.zoom.us/docs/api-reference/phone/methods/#operation/getCallLogDetails
        """
        return self.make_request(
            end_point=PHONE_CALL_LOG_DETAIL.format(call_log_id=call_log_id)
        )

    def list_phone_recordings(self, call_id: str) -> dict:
        """
        Request all recordings under caller id.
        https://marketplace.zoom.us/docs/api-reference/phone/methods/#operation/getPhoneRecordingsByCallIdOrCallLogId
        :param call_id: Caller Id
        :return: [
            # Referred to call_logs.json file under temp_utils folder
        ]
        """
        return self.make_request(
            end_point=PHONE_RECORDINGS.format(call_id=call_id),
        )

    def list_meeting_recordings(self, meeting_id: str) -> dict:
        """
        https://marketplace.zoom.us/docs/api-reference/zoom-api/methods/#operation/recordingGet
        """
        return self.make_request(
            end_point=MEETINGS_RECORDINGS.format(meeting_id=meeting_id),
        )

    def call_download_transcript(self, recording_id: str) -> dict:
        """
        Use this API to download the phone recording transcript.
        https://marketplace.zoom.us/docs/api-reference/phone/methods/#operation/phoneDownloadRecordingTranscript
        :param recording_id: The phone recording ID
        :return: {
            # Referred to phone_transcript.json file under temp_utils folder
        }
        """
        self._request_token()
        return self.make_request(
            end_point=PHONE_TRANSCRIPT_DOWNLOAD.format(recording_id=recording_id)
        )

    @error_handler
    def generate_cdr_transcript_recording_data_call(
        self, call_id: str
    ) -> Optional[ZoomDTO]:
        """
        BLOB CALL (ZoomDTO): CDR / TRANSCRIPT / RECORDING
        """
        logger.info(f" Call ID {call_id} Generating Blob")

        raw_call_log_detail = [
            call_detail
            for call_detail in self.call_logs
            if call_detail["id"] == call_id
        ]
        call_log_detail: dict = raw_call_log_detail[0] if raw_call_log_detail else None

        if call_log_detail is None:
            return None

        persona_details: dict = self.user_detail(call_log_detail.get("user_id"))
        logger.debug(f" Call Log Detail {call_log_detail}")

        cdr_details: CDR = generate_cdr_call(persona_details, call_log_detail)
        timeline = self.call_download_transcript(call_log_detail["recording_id"])
        transcript_available = (
            timeline if timeline is not None else _empty_transcript(call_id)
        )

        transcript_details: Transcript = generate_transcript_call(
            transcript_available, call_id
        )
        recording_details: Recording = generate_recording_call(
            self.list_phone_recordings(call_id), call_id
        )

        call_blob: ZoomDTO = ZoomDTO(
            cdr=cdr_details,
            transcript=transcript_details,
            recording=recording_details,
        )

        logger.info(f" Extracted CALL_BLOB {call_blob.cdr.source.source_id} FINISHED")
        return call_blob

    @error_handler
    def generate_cdr_transcript_recording_data_meet(self, meet_ids: list) -> ZoomDTO:
        """
        BLOB MEET (ZoomDTO): CDR / TRANSCRIPT / RECORDING
        """
        _participants: list = []
        parent_meet_id: int = meet_ids[0]  # E.G. 84065432222
        instance_meet_uuid: str = meet_ids[1]  # 'aiaR1KSbSfuY25fTmDuqoA=='

        logger.info(
            f"Meet UUID {instance_meet_uuid} Generating Blob from Meeting ID {parent_meet_id}"
        )

        if "/" in instance_meet_uuid:
            instance_meet_uuid: str = encoder.quote(instance_meet_uuid, safe="")
            instance_meet_uuid: str = encoder.quote(
                instance_meet_uuid, safe=""
            )  # Zoom API needs double encoding if '/'

        meet_details: dict = self.meeting_detail(parent_meet_id)
        if not meet_details:
            meet_details: dict = self.meeting_detail(instance_meet_uuid)
        logger.debug(f"Meet Detail {meet_details}")

        host_details: dict = self.user_detail(meet_details["host_id"])
        logger.debug(f"User Host {host_details}")

        _participants: list = self.past_meeting_participants(parent_meet_id)[
            "participants"
        ]
        participants: list = (
            _participants
            or self.past_meeting_participants(instance_meet_uuid)["participants"]
        )
        logger.debug(f"Participants Details {participants}")

        if participants:
            for participant in participants:
                participant["name"].replace("'", "")

        cdr_details: CDR = generate_cdr_meet(meet_details, host_details, participants)
        logger.debug(f"CDR Details {cdr_details}")

        meet_recordings: list = self.list_meeting_recordings(instance_meet_uuid).get(
            "recording_files", ""
        )
        transcript, audio = is_transcript_audio_recordings(meet_recordings)
        logger.debug(f"Transcript Details {transcript}")

        transcript_details: Transcript = generate_transcript_meet(
            transcript, instance_meet_uuid
        )
        recording_details: Recording = generate_recording_meet(
            audio, instance_meet_uuid
        )
        logger.debug(f"Recording Details {recording_details}")

        return ZoomDTO(
            cdr=cdr_details, transcript=transcript_details, recording=recording_details
        )

    @error_handler
    def ingest(self, init_step: bool = True) -> None:
        self.call_logs: list = self.list_calls_logs()

        if init_step:
            self._ingest_ids_calls()
            self._ingest_ids_meets()

            logger.info(
                f"Zoom Ingest fetched # {len(self.meet_ids)} Meets | # {len(self.call_logs_ids)} Calls"
            )

    @error_handler
    def _ingest_ids_calls(self):
        for call in self.call_logs:
            try:  # ONLY CALLS with cloud recordings
                if self.call_download_transcript(call["recording_id"]):
                    self.call_logs_ids.append(call["id"])
                    logger.debug(f"Adding call ID: {call['id']} ")
            except:
                continue  #  Zoom may have resource deleted!
        logger.debug(
            f"Zoom Ingesting Call Logs for IDs # {len(self.call_logs_ids)}| {self.call_logs_ids}"
        )

    @error_handler
    def _ingest_ids_meets(self):  # ONLY MEETS with cloud recordings
        self.meetings_with_recordings: list = self._generate_meetings_with_recordings()
        self._iterate_over_account_meetings(self.meetings_with_recordings)
        logger.debug(
            f"Zoom Ingesting Meet Details for IDs # {len(self.meet_ids)}| {self.meet_ids}"
        )

    def _generate_meetings_with_recordings(self) -> list:
        self.users_info, self.user_ids = self.list_users()
        return [self.list_meetings_recordings(user) for user in self.user_ids.values()]

    def _iterate_over_account_meetings(self, list_meetings_per_user: list):
        for list_of_meetings in list_meetings_per_user:
            for meet in list_of_meetings:
                if meet.get(
                    "recording_files", False
                ):  # to remove when AWS transcribe is active
                    self._get_meet_identifiers(meet)

    def _get_meet_identifiers(self, meet: dict):
        if cloud_recording := self._has_recording(meet):
            meet_id: int = meet.get("id")
            recording_uuid: str = cloud_recording["meeting_id"]
            logger.info(f"Meet ID {meet_id} has recording {recording_uuid} ")
            self.meet_ids.append((meet_id, recording_uuid))

    def _has_recording(self, meet: dict):
        cloud_recording = [
            recording
            for recording in meet.get("recording_files")
            if "VTT" in recording["file_extension"]
        ]
        return cloud_recording[0] if len(cloud_recording) else False


# test = ZoomAPI('melqart', start_date='2022-11-24', end_date='2022-11-25')
