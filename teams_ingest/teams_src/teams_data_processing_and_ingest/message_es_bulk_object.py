"""
This object holds a list of each item in a teams conversation.
it is used for the es Bulk upload process
"""
import logging
import sys
from typing import Dict, List

from teams_src.teams_data_processing_and_ingest.elastic_search.es_teams_index import (
    TEAMS,
    teams_id,
)

log = logging.getLogger()


def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum(get_size(v, seen) for v in obj.values())
        size += sum(get_size(k, seen) for k in obj.keys())
    elif hasattr(obj, "__dict__"):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum(get_size(i, seen) for i in obj)
    return size


class ConversationAudience:
    def __init__(self):
        self._user_list: List[teams_id] = []

    @property
    def userList(self):
        return self._user_list

    # Add a user to the participants for a Message or Attachment
    def add_user(self, new_user: teams_id) -> None:
        if not [x for x in self._user_list if x.uuid == new_user.uuid]:
            try:
                self._user_list.append(new_user)
                log.debug(f"Added {new_user.fullname} to audience")
            except Exception as ex:
                log.exception(ex)
        else:
            log.debug(f"User {new_user.fullname} already in audience")

    # Remove a user from the participants list for a Message
    def remove_user(self, user: teams_id) -> None:
        # if [x for x in user_list if x["LoginName".lower()] == user["LoginName".lower()]]:
        for find_user in self._user_list:
            if find_user.uuid == user.uuid:
                try:
                    self._user_list.remove(find_user)
                    log.debug(f"Removed {find_user.fullname} from audience")
                except ValueError as ex:
                    log.debug(f"{find_user.fullname} not found in audience")

    def get_to_list(self, messageFrom: teams_id) -> List[teams_id]:
        to_list: List[teams_id] = [x for x in self._user_list if x.uuid != messageFrom.uuid]
        if not to_list:
            log.debug("No Users in the TO list which is OK for the first message but odd after that!")
            return []
        return to_list


class TeamsBulkMessages:
    def __init__(self) -> None:
        self._list_of_teams_messages: List[Dict] = []
        self._msg_count: int = 0
        self._msg_list_size: int = 0

    @property
    def listOfConversationItems(self) -> List[Dict]:
        return self._list_of_teams_messages

    @property
    def bulkListCount(self) -> int:
        return self._msg_count

    @property
    def bulkListSize(self):
        return self._msg_list_size

    def add_teams_message(self, teams_message: TEAMS) -> None:
        self._list_of_teams_messages.append(teams_message.to_dict())
        self._msg_count += 1
        self._msg_list_size += get_size(teams_message)
