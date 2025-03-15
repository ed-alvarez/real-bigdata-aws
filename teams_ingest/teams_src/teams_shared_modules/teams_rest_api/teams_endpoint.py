"""
Test for import teams-ingest
https://docs.microsoft.com/en-gb/azure/active-directory/develop/scenario-daemon-app-configuration?tabs=python
"""
import base64
import logging
import pprint
from datetime import datetime
from typing import ByteString, Dict, List

from teams_settings import uPNList
from teams_src.teams_shared_modules.file_handling import FileHandling
from teams_src.teams_shared_modules.teams_data_classes import ClientCreds, TeamsChannels
from teams_src.teams_shared_modules.teams_rest_api.get_teams_data import TeamsDataGrab
from teams_src.teams_shared_modules.teams_rest_api.msal_token import MSALToken

log = logging.getLogger(__name__)


class TeamsEndpoint:
    def __init__(self, clientCreds: ClientCreds) -> None:

        self._ms_app: MSALToken = MSALToken(Tenant_ID=clientCreds.tenant_id, Client_ID=clientCreds.clientID, Secret=clientCreds.secret)

    def _filter_users_with_im_address(self, raw_user_list: List[Dict]) -> List[Dict]:
        users_with_im_addresses: List[Dict] = [d for d in raw_user_list if (len(d["imAddresses"]) >= 1)]
        return users_with_im_addresses

    # {HTTP method} https://graph.microsoft.com/{version}/{resource}?{query-parameters}

    def _file_url_to_sharing_token(self, file_url: str) -> str:
        # https://docs.microsoft.com/en-us/graph/api/shares-get?view=graph-rest-1.0&tabs=http
        url_bytes: bytes = file_url.encode("UTF-8")
        base_64_url_bytes: bytes = base64.b64encode(url_bytes)
        tidy_b64: bytes = base_64_url_bytes.rstrip(b"=").replace(b"/", b"_").replace(b"+", b"-")
        return_url: str = f"u!{tidy_b64.decode()}"
        return return_url

    def get_file(self, file_url: str):
        sharing_token: str = self._file_url_to_sharing_token(file_url=file_url)
        url: str = f"https://graph.microsoft.com/beta/shares/{sharing_token}/driveitem/content"
        data_grab: TeamsDataGrab = TeamsDataGrab(end_point=url, http_headers=self._ms_app.get_headers)
        data_grab.get_file()
        data: ByteString = data_grab.fileContent
        return data

    def get_image(self, image_full_url: str):
        data_grab: TeamsDataGrab = TeamsDataGrab(end_point=image_full_url, http_headers=self._ms_app.get_headers)
        data_grab.get_file()
        data: ByteString = data_grab.fileContent
        return data

    def get_all_users(self) -> List[Dict]:
        #        url: str="https://graph.microsoft.com/beta/users?$filter=accountEnabled eq true&$select=displayName,id,accountEnabled,userPrincipalName,mail,assignedLicenses.showInAddressList,userType"
        url: str = "https://graph.microsoft.com/beta/users?$filter=userType eq 'Member'"
        data_grab: TeamsDataGrab = TeamsDataGrab(end_point=url, http_headers=self._ms_app.get_headers)
        data_grab.get_data_all()
        data: List[Dict] = self._filter_users_with_im_address(raw_user_list=data_grab.teamsData)
        return data

    def get_members_of_a_chat(self, chat_id: str) -> List[Dict]:
        chat_id: str = chat_id or "19:0f97ac84-386f-41fe-9902-77beded8033a_9a618be6-2988-4202-84cf-634ecc976bf2@unq.gbl.spaces"
        url: str = f"https://graph.microsoft.com/beta/chats/{chat_id}/members"
        data_grab: TeamsDataGrab = TeamsDataGrab(end_point=url, http_headers=self._ms_app.get_headers)
        data_grab.get_data_all()
        data: List[Dict] = data_grab.teamsData
        return data

    def get_user_id_from_upn(self, uPN: str) -> Dict:
        url: str = f"https://graph.microsoft.com/beta/users/{uPN}"
        data_grab: TeamsDataGrab = TeamsDataGrab(end_point=url, http_headers=self._ms_app.get_headers)
        data_grab.get_single_data()
        data: Dict = data_grab.teamsData[0]
        return data


class UserChats(TeamsEndpoint):  # TODO This is the API Client
    def __init__(self, user_id: str, clientCreds: ClientCreds):
        super().__init__(clientCreds=clientCreds)
        self._user_id = user_id

    def _get_user_chats_endpoint(self) -> TeamsDataGrab:
        _id: str = self._user_id
        url: str = f"https://graph.microsoft.com/beta/users/{_id}/chats/allMessages"  # TODO Use Generic Make Request
        http_headers: Dict = self._ms_app.get_headers
        data_grab: TeamsDataGrab = TeamsDataGrab(end_point=url, http_headers=http_headers)
        return data_grab

    def get_chat_from(self, dt_start: datetime) -> List[Dict]:
        data_grab_obj: TeamsDataGrab = self._get_user_chats_endpoint()
        data_grab_obj.get_data_from(dt_start=dt_start)
        data: List[Dict] = data_grab_obj.teamsData
        return data

    def get_chat_history(self, dt_start: datetime, dt_end: datetime) -> List[Dict]:
        data_grab_obj: TeamsDataGrab = self._get_user_chats_endpoint()
        data_grab_obj.get_data_history(dt_start=dt_start, dt_end=dt_end)
        data: List[Dict] = data_grab_obj.teamsData
        return data

    def get_chat_previous_custom_period(self, time_delta_unit: str, time_delta_number: int) -> List[Dict]:
        data_grab_obj: TeamsDataGrab = self._get_user_chats_endpoint()
        data_grab_obj.get_data_previous_custom_period(time_delta_unit=time_delta_unit, time_delta_number=time_delta_number)
        data: List[Dict] = data_grab_obj.teamsData
        return data

    def get_chat_previous_day(self) -> List[Dict]:
        data_grab_obj: TeamsDataGrab = self._get_user_chats_endpoint()
        data_grab_obj.get_data_previous_day()
        data: List[Dict] = data_grab_obj.teamsData
        return data

    def get_chat_all_data(self) -> List[Dict]:
        data_grab_obj: TeamsDataGrab = self._get_user_chats_endpoint()
        data_grab_obj.get_data_all()
        data: List[Dict] = data_grab_obj.teamsData
        return data

    def get_todays_o365_messages_by_user_id(self) -> List[Dict]:
        # email Addresses NOT Teams
        id: str = self._user_id
        url: str = f"https://graph.microsoft.com/v1.0/users/{id}/messages"  # TODO Migrate to Constants
        data_grab: TeamsDataGrab = TeamsDataGrab(end_point=url, http_headers=self._ms_app.get_headers)
        data_grab.get_data_previous_day()
        data: List[Dict] = data_grab.teamsData
        return data


class ChannelChats(TeamsEndpoint):
    def __init__(self, clientCreds: ClientCreds):
        super().__init__(clientCreds=clientCreds)

    def get_all_groups(self) -> List[Dict]:
        url = "https://graph.microsoft.com/v1.0/groups?$orderby=displayName"
        data_grab = TeamsDataGrab(end_point=url, http_headers=self._ms_app.get_headers)
        data_grab.get_data_all()
        data: List[Dict] = data_grab.teamsData
        return data

    def get_channels_by_team_id(self, team_id: str) -> List[Dict]:
        team_id = team_id or "1c0bd483-b913-4838-b14f-4ab278185cf7"
        url: str = f"https://graph.microsoft.com/beta/teams/{team_id}/channels"
        data_grab: TeamsDataGrab = TeamsDataGrab(end_point=url, http_headers=self._ms_app.get_headers)
        data_grab.get_data_all()
        data: List[Dict] = data_grab.teamsData
        return data

    def get_messages_by_a_channel_in_a_team(self, team_id: str, channel_id: str) -> List[Dict]:
        team_id = team_id or "1c0bd483-b913-4838-b14f-4ab278185cf7"
        chanel_id: str = channel_id or "19:4b117827243140ffab2e9e6a5721be90@thread.skype"
        url: str = f"https://graph.microsoft.com/beta/teams/{team_id}/channels/{chanel_id}/messages"
        data_grab: TeamsDataGrab = TeamsDataGrab(end_point=url, http_headers=self._ms_app.get_headers)
        data_grab.get_data_all()
        data: List[Dict] = data_grab.teamsData
        return data

    def get_delta_messages_by_a_channel_in_a_team(self, team_id: str, channel_id: str) -> List[Dict]:
        team_id = team_id or "1c0bd483-b913-4838-b14f-4ab278185cf7"
        chanel_id: str = channel_id or "19:4b117827243140ffab2e9e6a5721be90@thread.skype"
        url: str = f"https://graph.microsoft.com/beta/teams/{team_id}/channels/{chanel_id}/messages/delta"
        data_grab: TeamsDataGrab = TeamsDataGrab(end_point=url, http_headers=self._ms_app.get_headers)
        data_grab.get_delta_last_day_data()
        data: List[Dict] = data_grab.teamsData
        return data

    def get_message_replies(self, team_id: str, channel_id: str, message_id: str) -> List[Dict]:
        team_id = team_id or "1c0bd483-b913-4838-b14f-4ab278185cf7"
        chanel_id: str = channel_id or "19:4b117827243140ffab2e9e6a5721be90@thread.skype"
        message_id = message_id or "1608580202835"
        url: str = f"https://graph.microsoft.com/beta/teams/{team_id}/channels/{chanel_id}/messages/{message_id}/replies"
        data_grab: TeamsDataGrab = TeamsDataGrab(end_point=url, http_headers=self._ms_app.get_headers)
        data_grab.get_data_all()
        data: List[Dict] = data_grab.teamsData
        return data


if __name__ == "__main__":
    import boto3

    CLIENT = "ips"
    ssm = boto3.client("ssm")
    TENANT_ID = ssm.get_parameter(Name=f"/teams/{CLIENT}/tenant_id")["Parameter"]["Value"]
    CLIENT_ID = ssm.get_parameter(Name=f"/teams/{CLIENT}/client_id")["Parameter"]["Value"]
    SECRET = ssm.get_parameter(Name=f"/teams/{CLIENT}/secret", WithDecryption=True)["Parameter"]["Value"]

    obj_teams_data = TeamsEndpoint(tenantID=TENANT_ID, clientID=CLIENT_ID, secret=SECRET)
    file_store = FileHandling()

    def UrlToSharingToken(inputUrl: str):
        url_bytes = inputUrl.encode("UTF-8")
        base_64_url_bytes = base64.b64encode(url_bytes)
        tidy_b64 = base_64_url_bytes.rstrip(b"=").replace(b"/", b"_").replace(b"+", b"-")
        return f"u!{tidy_b64.decode()}"

    def get_file(sharingToken):
        url = f"https://graph.microsoft.com/beta/shares/{sharingToken}/driveitem/content"
        result = obj_teams_data.get_file(url=url)
        pprint.pprint(result)

    def get_info():
        result = obj_teams_data.get_delta_messages_by_a_channel_in_a_team(
            team_id="940fe247-6fdc-497a-8565-cddd96e2e1d1",
            channel_id="19:a90939fa34244bb1ba6e5f219c3114cc@thread.tacv2",
        )
        pprint.pprint(result)

    def get_chats():
        ids = []
        for upn in uPNList:
            result = obj_teams_data.get_user_id_from_upn(uPN=upn)
            if "id" in result:
                ids.append(result["id"])
            else:
                log.warning(f"{upn} not found in o365")
                continue

        pprint.pprint(ids)

        messages = []
        for id in ids:
            if result := obj_teams_data.get_day_messages_by_id(user_id=id):
                filename = f"{id}.json"
                file_store.save_json(data=result)
                messages += result
            else:
                log.warning(f"No messages for {id}")
                continue

        pprint.pprint(messages)

    def get_teams():
        groups = []
        groups = obj_teams_data.get_all_groups()

        teams = []
        for group in groups:
            if result := obj_teams_data.get_channels_by_team_id(team_id=group["id"]):
                team = TeamsChannels()
                team.team_name = group["displayName"]
                team.team_id = group["id"]
                team.channel_list = result
                teams.append(team)
                pprint.pprint(result)
        pprint.pprint(teams)
        return teams

    def get_channel_chats(teams=""):

        messages = []
        for team in teams:
            for channel in team.channel_list:
                if message_result := obj_teams_data.get_delta_messages_by_a_channel_in_a_team(
                    team_id=team.team_id, channel_id=channel["id"]
                ):
                    messages += message_result
                    for item in message_result:
                        if replies_result := obj_teams_data.get_message_replies(
                            team_id=team.team_id,
                            channel_id=channel["id"],
                            message_id=item["id"],
                        ):
                            messages += replies_result
                pprint.pprint(messages)

        pprint.pprint(messages)

        messages = []

        return

    # from teams_tests.data import list_of_channels
    # get_channel_chats(teams=list_of_channels.channels)

    url = "https://ipsentinelltd-my.sharepoint.com/personal/mike_ip-sentinel_com1/Documents/Microsoft Teams Chat Files/Screenshot 2021-01-27 at 12.23.40.png"
    sharing_token = UrlToSharingToken(inputUrl=url)

    get_file(sharing_token)
