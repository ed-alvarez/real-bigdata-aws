import json
import os

import helpers.s3
import pytest
import settings
import slack_parse.ingest_helpers.slack_download_common

CLIENT_NAME = "ips"


def test_determine_save_locations():
    date_y_m_d = "2300-24-24"
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    (local_path, s3_sub_folder,) = slack_parse.ingest_helpers.slack_download_common._determine_save_locations(
        s3, "users", date_y_m_d, "channel_id", "channel_name"
    )
    print(local_path, s3_sub_folder)
    assert s3_sub_folder == "json-slack"
    assert local_path == os.path.join(settings.TEMPDIR, "users.json")


def test_determine_save_locations_with_unknown_type():
    with pytest.raises(NotImplementedError):
        (
            local_path,
            s3_sub_folder,
        ) = slack_parse.ingest_helpers.slack_download_common._determine_save_locations(None, "invalid type", "", "", "")


def test_archive_data_users_file():
    data = {"U123": {"name": "example"}}
    date_y_m_d = "2000-01-01"
    s3_file_original = "dev.archived.slack/2000-01-01/json-slack/users.json"
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    s3.delete_file(s3_file_original)
    s3_file_return = slack_parse.ingest_helpers.slack_download_common.archive_data(CLIENT_NAME, data, "users", date_y_m_d)
    assert s3_file_return == s3_file_original
    contents = json.loads(s3.get(s3_file_return))
    assert "U123" in contents
    s3.delete_file(s3_file_return)
