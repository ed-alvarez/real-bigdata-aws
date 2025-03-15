import sys
from pathlib import Path

tenant_directory = Path(__file__).resolve().parent.parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))

import logging
from typing import Dict, List

from teams_settings import INGEST_SOURCE
from teams_src.teams_data_fetch_conversation.event_date_helper_functions import (
    parse_event_for_period,
)
from teams_src.teams_shared_modules.step_funtion_data_classes import TeamsEvent
from teams_src.teams_shared_modules.teams_data_classes import (
    ClientCreds,
    TeamsDateRange,
)
from teams_src.teams_shared_modules.teams_rest_api.teams_endpoint import UserChats

from shared.shared_src.s3.s3_helper import S3Helper

logging.basicConfig(
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger()


class ConversationFetcher:
    def __init__(
        self,
        event: TeamsEvent,
        client_creds: ClientCreds = None,
    ):
        self._event: TeamsEvent = event
        self._client_creds = client_creds or ClientCreds(firm=self._event.firm, tenant_id=self._event.tenant_id)
        self._s3_client: S3Helper = S3Helper(
            client_name=self._event.firm,
            ingest_type=INGEST_SOURCE,
        )

    def one_to_one_chats(self):
        list_of_files_to_process: List = []

        if self._event.user_ids:
            user_id = self._event.user_ids.pop()

            log.info(f"Using creds for MS Teams fetching {self._client_creds}")

            list_of_dates_to_process: List[TeamsDateRange] = parse_event_for_period(event=self._event)

            log.info(f"List of dates to process {list_of_dates_to_process}")

            user_total_msg = 0

            for teams_date in list_of_dates_to_process:
                log.info(f"Processing {teams_date} Chats Object for user {user_id}")

                teams_chats_obj: UserChats = UserChats(user_id=user_id, clientCreds=self._client_creds)
                user_messages_on_date: List[Dict] = []

                try:
                    user_messages_on_date = teams_chats_obj.get_chat_history(
                        dt_start=teams_date.search_from, dt_end=teams_date.search_to
                    )

                except Exception as ex:
                    log.exception(f"ERROR extracting data for user {user_id} on {teams_date}")

                qty_messages = len(user_messages_on_date)
                user_total_msg += qty_messages

                if user_total_msg:

                    log.info(f"{qty_messages} messages for user {user_id} on {teams_date.from_str()}")

                    try:
                        log.debug("saving messages to S3")
                        s3_uri_user_messages_one_day = (
                            self._s3_client.lamda_write_to_s3(  # Use batch write (IDK if we have available as of now)
                                date_from_event=teams_date.search_from,
                                obj=user_messages_on_date,
                                file_name=f"user_{user_id}_{teams_date.from_str()}",
                            )
                        )
                        list_of_files_to_process.append(s3_uri_user_messages_one_day)
                    except Exception as ex:
                        log.exception("ERROR saving messages to S3")
                        raise ex

        return list_of_files_to_process
