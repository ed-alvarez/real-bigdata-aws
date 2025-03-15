import datetime
import logging
import sys
from pathlib import Path
from typing import List

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_src.teams_data_download.user_chats_process import IngestUsersToProcess
from teams_src.teams_shared_modules.step_funtion_data_classes import TeamsEvent
from teams_src.teams_shared_modules.teams_data_classes import (
    ClientCreds,
    DynamoClientRecord,
)

log = logging.getLogger()


class GrabUserTeamIDs:
    def __init__(
        self,
        event: TeamsEvent,
        dynamo_client_record: DynamoClientRecord = None,
        client_creds: ClientCreds = None,
    ):
        self._event: TeamsEvent = event
        self._dynamo_client_record: DynamoClientRecord = (
            dynamo_client_record or DynamoClientRecord(client=self._event.tenant_name).get_dynamo_client()
        )
        self._client_creds = client_creds or ClientCreds(firm=self._event.firm, tenant_id=self._event.tenant_id)

    def _get_users_to_download(self, event: TeamsEvent) -> List:
        log.info("Start One to one chat processing")

        log.debug("setup user list object")
        teams_users_obj: IngestUsersToProcess = IngestUsersToProcess(
            event=event, dynamo_client_record=self._dynamo_client_record, client_creds=self._client_creds
        )
        try:
            user_id_list: List[str] = teams_users_obj.get_user_list()
            log.debug(f"List of users to process : {user_id_list}")
        except Exception as ex:
            log.exception("ERROR in processing user list")
            raise ex

        return user_id_list

    def get_users_ids(self, s3_client) -> List:
        user_ids = self._get_users_to_download(event=self._event)
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        date_event = datetime.datetime.now() if self._event.period == "daily" else self._event.start_date
        s3_client.lamda_write_to_s3(
            date_from_event=date_event,
            obj=dict(zip(["user_ids"], user_ids)),
            file_name=f"user_ids_downloaded_at_{now}",
        )
        self._event.user_ids = user_ids
        return self._event.user_ids
