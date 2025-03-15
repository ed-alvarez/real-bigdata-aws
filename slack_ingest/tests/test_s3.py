import os
from datetime import datetime

import boto3
import helpers.s3
import pytest
import slack_parse.download_api.slack_api_downloader
from helpers.s3 import S3

date_y_m_d = datetime.now().strftime("%Y-%m-%d")
CLIENT_NAME = "ips"


def test_s3_init():
    s3 = S3(CLIENT_NAME, date_y_m_d)
    assert s3 is not None
    assert "helpers.s3.S3" in str(s3)


def test_s3_upload_test_file():
    testfile = "/tmp/testfileforslacks3moduletesting"
    file_contents = "012345678910\nhello"
    with open(testfile, "w+") as f:
        f.write(file_contents)

    s3 = S3(CLIENT_NAME, date_y_m_d)
    s3.upload_files_to_s3_todo_and_archived_subfolder([testfile], "test")
    s3_boto = boto3.client("s3")
    bucket_name = f"{CLIENT_NAME}.ips"
    testfilename = os.path.basename(testfile)
    if os.environ.get("STAGE") == "dev" or os.environ.get("AWS_EXECUTION_ENV") is None:
        key_prefix = "dev."
    todo_key = f"{key_prefix}todo.slack/{date_y_m_d}/test/{testfilename}"
    archived_key = f"{key_prefix}archived.slack/{date_y_m_d}/test/{testfilename}"

    s3_object = s3_boto.get_object(Bucket=bucket_name, Key=todo_key)
    body = s3_object["Body"]
    todo_text = body.read().decode("utf-8")
    assert todo_text == file_contents
    s3_object = s3_boto.get_object(Bucket=bucket_name, Key=archived_key)
    body = s3_object["Body"]
    archived_text = body.read().decode("utf-8")
    assert archived_text == file_contents

    s3.delete_file(todo_key)
    s3.delete_file(archived_key)


def test_check_metadata_file_exists():
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    sd.download_all_data()
    s3 = S3(CLIENT_NAME, date_y_m_d)
    metadata_file_path = os.path.join("json-slack", "channels.json")
    assert s3.check_metadata_file_exists(filename=metadata_file_path)


def test_has_metadata():
    date_y_m_d = "2020-12-23"
    s3 = S3(CLIENT_NAME, date_y_m_d)
    channels, users = s3.get_metadata()
    assert channels is not None and users is not None
    print(channels, users)
    # Test for not present
    date_y_m_d = "2019-12-23"
    s3 = S3(CLIENT_NAME, date_y_m_d)
    channels, users = s3.get_metadata()
    assert channels is None and users is None
    # assert (not s3.has_metadata())


def test_get_messages_paths_from_archived():
    s3 = S3(CLIENT_NAME, "2021-01-21")
    paths = s3.get_messages_paths_from_archive()
    print(paths)
    si_path = "dev.archived.slack/2021-01-21/json-slack/messages/C01FHG8T7J5__slack-ingest/2021-01-21.json"
    slackbot_path = "dev.archived.slack/2021-01-21/json-slack/messages/DPE3CD7CY/2021-01-21.json"
    assert si_path in paths
    assert slackbot_path in paths


def test_get_messages_paths_from_todo():
    this_date_y_m_d = "2021-01-22"
    s3 = S3(CLIENT_NAME, this_date_y_m_d)
    paths = s3.get_messages_paths_from_todo()
    if len(paths) == 0:  # Re-download
        sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
        sd.download_all_data(this_date_y_m_d)
        paths = s3.get_messages_paths_from_todo()
    # Check to see if paths present in s3_messages_paths
    si_path = "dev.todo.slack/2021-01-22/json-slack/messages/C01FHG8T7J5__slack-ingest/2021-01-22.json"
    sb_path = "dev.todo.slack/2021-01-22/json-slack/messages/DPE3CD7CY/2021-01-22.json"
    assert si_path in paths
    assert sb_path in paths
    print(paths)


def test_s3_file_exists_exception():
    with pytest.raises(Exception) as e_info:
        helpers.s3.s3_file_exists(None, "ips.ips", "nokey")
        print(e_info)


def tes_s3_delete_file_raises_error():
    # This test doesn't work as deleting a non existent object is fine with s3
    s3 = S3(CLIENT_NAME, "2021-02-25")
    ret = s3.delete_file("nosuchkey")
    print(ret)
    # with pytest.raises(Exception) as e_info:
    #    s3.delete_file('nosuchkey')


def test_s3_copy_file_raises_error():
    s3 = S3(CLIENT_NAME, "2021-02-25")
    with pytest.raises(Exception) as e_info:
        s3.copy_file("nosuchkey", "nosuchotherkey")
    assert "NoSuchKey" in str(e_info.value)
