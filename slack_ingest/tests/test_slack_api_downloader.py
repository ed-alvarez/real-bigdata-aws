import json
from pprint import pprint

import helpers.s3
import mock
import pytest
import settings
import slack
import slack_parse.download_api.slack_api_downloader
from slack_parse.download_api.slack_api_downloader import SlackData

CLIENT_NAME = "ips"


def test_get_users():
    sd = SlackData(CLIENT_NAME)
    users = sd.get_users()
    assert users is not None
    pprint(users)


def test_get_conversations_lists():
    sd = SlackData(CLIENT_NAME)
    conversations = sd.get_conversations_list()
    assert conversations is not None
    pprint(conversations)


def test_get_channels_with_members():
    sd = SlackData(CLIENT_NAME)
    cl_wm = sd.get_conversations_lists_with_members()
    assert cl_wm is not None
    channel_found = False
    for c in cl_wm:
        if c["id"] == "CP19UKSF4":
            channel_found = True
            print(c["members"])
            assert len(c["members"]) > 2
    assert channel_found
    pprint(cl_wm)


def test_get_messages():
    sd = SlackData(CLIENT_NAME)
    oldest_ts = "2020-10-15T24:00:00"
    latest_ts = "2020-12-22T00:00:00"
    messages = sd.get_messages(channel="C01FHG8T7J5", oldest=oldest_ts, latest=latest_ts)
    assert messages is not None
    pprint(messages)


# def test_download_attachments():
#    sd = SlackData(CLIENT_NAME)
#    assert sd["ok"] is True
#    # todo


def test_download_all_data_for_specific_date():
    sd = SlackData(CLIENT_NAME)
    # download yesterday
    # sd.download_conversations()
    # oldest = '2020-12-21T00:00:00'
    # latest = '2020-12-21T24:00:00'
    date_y_m_d = "2020-12-21"
    data = sd.download_all_data(date_y_m_d, force=True)
    assert data["messages_s3_paths"] is not None


def test_download_all_data_for_yesterday():
    sd = SlackData(CLIENT_NAME)
    results = sd.download_all_data(force=True)
    pprint(results)
    assert "messages_s3_paths" in results
    # Will always have the slack export bot message
    assert len(results["messages_s3_paths"]) > 0


def test_lambda_method():
    event = {"client_name": "ips", "date_y_m_d": "2021-02-23"}
    results = slack_parse.download_api.slack_api_downloader.download_slack_from_lambda_event(event)
    print(results)
    slack_ingest_channel_json = "dev.todo.slack/2021-02-23/json-slack/messages/C01FHG8T7J5__slack-ingest/2021-02-23.json"
    assert len(results["messages_s3_paths"]) > 0
    assert slack_ingest_channel_json in results["messages_s3_paths"]


def test_slack_connect_with_wrong_api_token():
    sd = SlackData(CLIENT_NAME)
    sd.slack_client = slack.WebClient(token="wrong-token", ssl=sd.ssl_context)
    with pytest.raises(Exception) as e_info:
        resp = sd.try_connect_to_slack()
        print(resp)
    assert "invalid_auth" in str(e_info)


def test_get_informative_error_msg_from_slack_api_error():
    e = mock.MagicMock()
    e.response.data = {
        "error": "missing_scope",
        "needed": "user:read",
        "provided": "none",
    }
    error_msg = slack_parse.download_api.slack_api_downloader._get_informative_error_msg_from_slack_api_error(e)
    print(error_msg)
    assert error_msg == "Missing Permission - Permission required = user:read  Current permissions = none"


def test_get_informative_error_msg_from_slack_api_error_not_perms():
    e = mock.MagicMock()
    e.response.data = {
        "error": "another general error",
        "needed": "user:read",
        "provided": "none",
    }
    error_msg = slack_parse.download_api.slack_api_downloader._get_informative_error_msg_from_slack_api_error(e)
    print(error_msg)
    assert error_msg == "another general error"


def test_get_members_for_empty_channel_returns_empty_list_exception_caught():
    channel_id = "C01QP7ZGNRF"  # Testing channel with no members in it
    sd = SlackData(CLIENT_NAME)
    members = sd.get_conversations_members(channel_id)
    print(members)
    assert len(members) == 0


def test_get_users_batch(monkeypatch):
    SLACK_API_LIMIT_SIZE = 2
    monkeypatch.setattr(settings, "SLACK_API_LIMIT_SIZE", SLACK_API_LIMIT_SIZE)
    date_y_m_d = "2021-02-23"
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    s3.delete_file(f"dev.todo.slack/{date_y_m_d}/json-slack/messages/C01FHG8T7J5__slack-ingest/{date_y_m_d}.json")
    sd = SlackData(CLIENT_NAME)
    sd.download_all_data(date_y_m_d)
    j = json.loads(s3.get(f"dev.todo.slack/{date_y_m_d}/json-slack/messages/C01FHG8T7J5__slack-ingest/{date_y_m_d}.json"))
    print(j)
    assert len(j) == 7
    assert j[6]["text"] == "17 in thread"
    assert j[0]["text"] == "20 in channel with attachments"
    assert len(j[0]["files"]) > 0

    # Test for skipped download (download file already in todo folder)
    # tested elsewhere
