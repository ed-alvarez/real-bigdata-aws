import os
import re
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List
from unittest import mock

import pytest
import responses
from aws_lambda_context import LambdaContext
from teams_src.teams_data_processing_and_ingest.teams_conversation.conversation_to_es import (
    ConvertConversation,
)
from teams_src.teams_shared_modules.teams_data_classes import (
    ClientCreds,
    DynamoClientRecord,
)
from teams_tests.data.stepfunction_data import teams_history_decode
from teams_tests.data.user_chat_big import user_chat_big

AWS_REGION = os.environ.get("AWS_Region", "eu-west-1")

CLIENT_NAME = "testing"
BUCKET_NAME = f"{CLIENT_NAME}.ips"

attachment_1: Dict = {
    "id": "7cc93d51-e5a2-492e-af3b-614a3da8f921",
    "contentType": "reference",
    "contentUrl": "https://ipsentinelltd-my.sharepoint.com/personal/mike_ip-sentinel_com1/Documents/Microsoft Teams Chat Files/Screenshot 2021-01-27 at 12.23.40.png",
    "content": None,
    "name": "Screenshot 2021-01-27 at 12.23.40.png",
    "thumbnailUrl": None,
}

attachment_list: List = [attachment_1]

contentUrl = "https://ipsentinelltd-my.sharepoint.com/personal/mike_ip-sentinel_com1/Documents/Microsoft Teams Chat Files/Screenshot 2021-01-27 at 12.23.40.png"

conversation_id = "text conversation"
date_time = datetime(2021, 1, 13, 00, 00, 00)


class TestHelper:
    @contextmanager
    def s3_setup(self, s3_client):
        bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": AWS_REGION})
        yield

    @pytest.fixture
    def conversation_obj(self, ssm_teams_setup):
        with ssm_teams_setup:
            client_creds: ClientCreds = ClientCreds(firm="test-ips", tenant_id="a38e65be-fb2c-4ab0-9084-199607af9f21")
            convert_conversation_obj = ConvertConversation(
                conversation=user_chat_big,
                aws_event=teams_history_decode,
                aws_context=LambdaContext(),
                client_creds=client_creds,
            )
        return convert_conversation_obj

    def test_remove_html_tags(self, conversation_obj):
        conversation_id = "text conversation"
        test_txt = '<div><div>OK, I think we can use the OrderingFilter: <a href="https://www.django-rest-framework.org/api-guide/filtering/#orderingfilter" rel="noreferrer noopener" target="_blank" title="https://www.django-rest-framework.org/api-guide/filtering/#orderingfilter">https://www.django-rest-framework.org/api-guide/filtering/#orderingfilter</a></div>\n</div>'
        result = conversation_obj._remove_html_tags(test_txt)
        assert "OK, I think we can use the OrderingFilter:" in result

    def test_get_attachment_and_save_to_file(self, teams_s3_client, conversation_obj, dynamo_db_teams_setup, teams_ddb_client):
        with mock.patch(
            "teams_src.teams_shared_modules.teams_data_classes.DynamoClientRecord.ddb_client",
            teams_ddb_client,
        ):
            with self.s3_setup(teams_s3_client):
                with responses.RequestsMock() as rsps:
                    rsps.add_passthru(re.compile("https://login.microsoftonline.com*"))
                    rsps.add_passthru(re.compile("https://graph.microsoft.com*"))
                    rsps.add_passthru(re.compile("https://ipsentinelltd-my.sharepoint.com*"))
                    rsps.add_passthru(re.compile("http://localhost*"))
                    _ = conversation_obj._parse_attachments(attachments=attachment_list, date_time=date_time)
                    _ = teams_s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="dev.processed.teams")

    def test_search_for_email(self, conversation_obj, dynamo_db_teams_setup, teams_ddb_client):
        uuid = "28ad04f7-55d2-4fe8-b917-52f3c24ab13d"
        with mock.patch(
            "teams_src.teams_shared_modules.teams_data_classes.DynamoClientRecord.ddb_client",
            teams_ddb_client,
        ):
            response = conversation_obj._search_for_email(uuid=uuid)
            assert response == "james@ip-sentinel.com"

    def testfirm_extract_user_from_message(self, teams_s3_client, conversation_obj, dynamo_db_teams_setup, teams_ddb_client):
        user_dict = {
            "id": "0343ab0a-2dee-4672-bc86-20af382ea5d8",
            "displayName": "Denny Biasiolli",
            "userIdentityType": "aadUser",
        }
        with mock.patch(
            "teams_src.teams_shared_modules.teams_data_classes.DynamoClientRecord.ddb_client",
            teams_ddb_client,
        ):
            response = conversation_obj._extract_user_from_message(user=user_dict)
            assert response.domain == "fingerprint-supervision.com"
            assert response.emailaddress == "denny@fingerprint-supervision.com"

    def test_extract_user_from_message_user_not_found(
        self, teams_s3_client, conversation_obj, dynamo_db_teams_setup, teams_ddb_client
    ):
        user_dict = {
            "id": "xxxxx-4672-bc86-20af382ea5d8",
            "displayName": "Denny Biasiolli",
            "userIdentityType": "aadUser",
        }
        with mock.patch(
            "teams_src.teams_shared_modules.teams_data_classes.DynamoClientRecord.ddb_client",
            teams_ddb_client,
        ):
            response = conversation_obj._extract_user_from_message(user=user_dict)
            assert response.domain == ""
            assert response.emailaddress == ""

    def test_format_message_time_to_datetime(self, conversation_obj):
        CASES = [
            ("2021-03-03T14:20:27Z", 3),
            ("2021-01-27T14:39:59.793Z", 1),
        ]

        for input, expected in CASES:
            response: datetime = conversation_obj._format_message_time_to_datetime(message_date=input)
            assert response.month == expected


"""
    def test_message_parse(self):
        json_message_1 = {
            "@odata.type": "#microsoft.graph.chatMessage",
            "id": "1636475360939",
            "replyToId": None,
            "etag": "1636475360939",
            "messageType": "message",
            "createdDateTime": "2021-11-09T16:29:20.939Z",
            "lastModifiedDateTime": "2021-11-09T16:29:20.939Z",
            "lastEditedDateTime": None,
            "deletedDateTime": None,
            "subject": "",
            "summary": None,
            "chatId": "19:28ad04f7-55d2-4fe8-b917-52f3c24ab13d_9a618be6-2988-4202-84gbl.spaces",
            "importance": "normal",
            "locale": "en-us",
            "webUrl": None,
            "channelIdentity": None,
            "policyViolation": None,
            "eventDetail": None,
            "from": {
                "application": None,
                "device": None,
                "user": {
                    "id": "9a618be6-2988-4202-84cf-634ecc976bf2",
                    "displayName": "Sean Morgan",
                    "userIdentityType": "aadUser"
                }
            },
            "body": {
                "contentType": "html",
                "content": "<attachment id=\"1636475319930\"></attachment>\n<p>Oakley dont need voice. \u00a338, 400 is email(110) and Teams(140)only </p> "
            },
            "attachments": [
                {
                    "id": "1636475319930",
                    "contentType": "messageReference",
                    "contentUrl": None,
                    "content": "{\"messageId\":\"1636475319930\",\"messagePreview\":\"well a bit more if they want voice transcriptions\",\"messageSender\": {\"application\":null,\"device\":null,\"user\": {\"userIdentityType\":\"aadUser\", \"id\":\"28ad04f7-55d2-4fe8-b917-52f3c24ab13d\",\"displayName\":\"James Hogbin\"}}}",
                    "name": None,
                    "thumbnailUrl": None
                }
            ],
            "mentions": [],
            "reactions": []
        }

        message_2 = {
            "@odata.type": "#microsoft.graph.chatMessage",
            "id": "1636456759989",
            "replyToId": None,
            "etag": "1636456759989",
            "messageType": "message",
            "createdDateTime": "2021-11-09T11:19:19.989Z",
            "lastModifiedDateTime": "2021-11-09T11:19:19.989Z",
            "lastEditedDateTime": None,
            "deletedDateTime": None,
            "subject": "",
            "summary": None,
            "chatId": "19:49e7c390-85fc-43ea-8d94-797e2c23f04f_9a618be6-2988-4202-84cf-634ecc976bf2@unq.gbl.spaces",
            "importance": "normal",
            "locale": "en-us",
            "webUrl": None,
            "channelIdentity": None,
            "policyViolation": None,
            "eventDetail": None,
            "from": {
                "application": None,
                "device": None,
                "user": {
                    "id": "9a618be6-2988-4202-84cf-634ecc976bf2",
                    "displayName": "Sean Morgan",
                    "userIdentityType": "aadUser"
                }
            },
            "body": {
                "contentType": "html",
                "content": "<attachment id=\"86e8a7fd-b44c-4fc4-997d-cc67713fa897\"></attachment>"
            },
            "attachments": [
                {
                    "id": "86e8a7fd-b44c-4fc4-997d-cc67713fa897",
                    "contentType": "reference",
                    "contentUrl": "https://ipsentinelltd-my.sharepoint.com/personal/sean_fingerprint-supervision_com/Documents/Microsoft Teams Chat Files/Screenshot 2021-11-09 at 11.08.49.png",
                    "content": None,
                    "name": "Screenshot 2021-11-09 at 11.08.49.png",
                    "thumbnailUrl": None
                }
            ],
            "mentions": [],
            "reactions": []
        }

"""
