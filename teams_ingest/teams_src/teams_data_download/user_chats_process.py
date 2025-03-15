import logging
from datetime import datetime
from operator import itemgetter
from typing import Dict, List

from teams_settings import Write_User_Data_To_File
from teams_src.teams_shared_modules.file_handling import FileHandling
from teams_src.teams_shared_modules.step_funtion_data_classes import TeamsEvent
from teams_src.teams_shared_modules.teams_data_classes import (
    ClientCreds,
    DynamoClientRecord,
    DynamoTeamsUser,
)
from teams_src.teams_shared_modules.teams_rest_api.teams_endpoint import (
    TeamsEndpoint,
    UserChats,
)

log = logging.getLogger()


class ProcessChats:
    pass


class GetChatsForUsers:
    def __init__(self, user_id_list: List[str], client_creds: ClientCreds) -> None:
        self._user_id_list: List[str] = user_id_list
        self._client_creds: ClientCreds = client_creds

    def get_conversations_and_archive(self) -> List[Dict]:

        file_store: FileHandling = FileHandling()
        messages: List[Dict] = []
        for id in self._user_id_list:
            obj_teams_data: UserChats = UserChats(user_id=id, clientCreds=self._client_creds)
            if result := obj_teams_data.get_chat_previous_day():
                if Write_User_Data_To_File:
                    filename: str = f"{id}.json"
                    file_store.save_json(data=result)
                messages += result
            else:
                log.warning(f"No messages for {id}")
                continue

        return messages


class IngestUsersToProcess:
    def __init__(
        self,
        event: TeamsEvent,
        dynamo_client_record: DynamoClientRecord = None,
        client_creds: ClientCreds = None,
    ) -> None:
        self.event: TeamsEvent = event
        self._dynamo_client_record: DynamoClientRecord = (
            dynamo_client_record or DynamoClientRecord(client=self.event.tenant_name).get_dynamo_client()
        )
        self._uPN_list: List = []
        self._client_creds: ClientCreds = client_creds or ClientCreds(firm=self.event.account)

    @property
    def dynamoClientRecord(self) -> DynamoClientRecord:
        return self._dynamo_client_record

    def _convert_user_record_from_teams_to_dyanmo(self, teams_user) -> DynamoTeamsUser:
        return DynamoTeamsUser(iD=teams_user["id"], uPN=teams_user["userPrincipalName"], date_added=datetime.now())

    def _convert_teams_to_dynamo_user(self, teams_user_list: List[Dict]) -> List[DynamoTeamsUser]:
        dynamo_user_list: List[DynamoTeamsUser] = []
        for user in teams_user_list:
            dynamo_user = self._convert_user_record_from_teams_to_dyanmo(teams_user=user)
            dynamo_user_list.append(dynamo_user)
        return dynamo_user_list

    def _detect_new_users(self, client_records: List[DynamoTeamsUser], users_to_process: List) -> List[DynamoTeamsUser]:
        users_to_process_dynamo: List[DynamoTeamsUser] = self._convert_teams_to_dynamo_user(teams_user_list=users_to_process)
        new_users: List[DynamoTeamsUser] = [
            user for user in users_to_process_dynamo if user.iD not in map(itemgetter("iD"), client_records)
        ]
        return new_users

    def _remove_exluded_users(self, user_list: List, excluded_users: set) -> List[Dict]:
        processed_list: List = [d for d in user_list if d.get("userPrincipalName").lower() not in excluded_users]
        return processed_list

    def _update_dynamo_users(self, new_users: List[DynamoTeamsUser]) -> None:
        for user in new_users:
            self._dynamo_client_record.users.append(user)
        self._dynamo_client_record.put_dynamo_client()
        return

    def _get_api_UPN_List_for_client(self) -> List[Dict]:
        obj_teams_data: TeamsEndpoint = TeamsEndpoint(clientCreds=self._client_creds)
        users: List[Dict] = obj_teams_data.get_all_users()
        return users

    def get_user_list(self) -> List[str]:
        """
        Get Users to process
            - get client record from Dynamo
            - get users from teams API
            - remove users in the client excluded list
            - update user record with any additional users plus date
            - return list of uIDs for processing
        """

        # Get User list from MS Teams API
        teams_api_users: List[Dict] = self._get_api_UPN_List_for_client()

        user_list_to_process: List[Dict] = teams_api_users

        # If there are exlusions remove them from the list
        if self._dynamo_client_record.excluded:
            user_list_to_process: List[Dict] = self._remove_exluded_users(
                user_list=teams_api_users, excluded_users=self._dynamo_client_record.excluded
            )

        if new_users := self._detect_new_users(
            client_records=self._dynamo_client_record.users,
            users_to_process=user_list_to_process,
        ):
            self._update_dynamo_users(new_users=new_users)

        # exctract the id field from the list and return just a list of ids
        user_list: List[str] = [user["id"] for user in user_list_to_process]

        return user_list


if __name__ == "__main__":
    event = TeamsEvent(client="ips", source="fred", period="xxx")
    obj = IngestUsersToProcess(event=event)
    ret = obj.get_user_list()
