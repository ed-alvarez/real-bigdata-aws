import json

import settings
import slack_parse.download_api.slack_api_downloader
import slack_parse.process.slack_processor

CLIENT_NAME = "ips"


def test_slack_processor_for_es_batch_size(monkeypatch):
    date_y_m_d = "2020-11-20"
    # Set environment variable before importing
    # os.environ['ES_UPLOAD_BATCH_SIZE'] = "2"
    # Set env variable using monkeypatch which will reset the value
    # once this test is done.
    # monkeypatch.setenv('ES_UPLOAD_BATCH_SIZE', "2") don't use env variables, just patch the variable itself
    monkeypatch.setattr(settings, "ES_UPLOAD_BATCH_SIZE", 2)

    # Remove last file of batch to make sure that it is created
    import helpers.s3

    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    s3.delete_file("dev.processed.slack/2020-11-20/json-processed/messages/C01FHG8T7J5__slack-ingest/2020-11-20__6-6.json")

    # Download data first
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    data = sd.download_all_data(date_y_m_d)
    print(data)

    # Process downloaded data
    p = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)
    assert p["ok"] is True
    assert p["num_messages_processed"] > 0  # always has slack daily export message
    last_message = s3.get("dev.processed.slack/2020-11-20/json-processed/messages/C01FHG8T7J5__slack-ingest/2020-11-20__6-6.json")
    last_message = json.loads(last_message)
    print(last_message)
    assert len(last_message) == 1
    last_message = last_message[0]
    assert "hello again" in last_message["_source"]["body"]


def test_slack_processor_for_es_batch_size_2(monkeypatch):
    date_y_m_d = "2021-02-10"
    last_file_s3_key = "dev.processed.slack/2021-02-10/json-processed/messages/C01FHG8T7J5__slack-ingest/2021-02-10__32-35.json"

    # Set environment variable before importing
    # os.environ['ES_UPLOAD_BATCH_SIZE'] = "2"
    # Use monkeypatch which will reset the value when done
    # monkeypatch.setenv('ES_UPLOAD_BATCH_SIZE', "2") # don't change env variables, just patch the setting itself.
    monkeypatch.setattr(settings, "ES_UPLOAD_BATCH_SIZE", 2)

    # Remove last file of batch to make sure that it is created
    import helpers.s3

    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    s3.delete_file(last_file_s3_key)

    # Download data first
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    data = sd.download_all_data(date_y_m_d)
    print(data)

    # Process downloaded data
    p = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)
    assert p["ok"] is True
    assert p["num_messages_processed"] > 0  # always has slack daily export message
    last_message = s3.get(last_file_s3_key)
    last_message = json.loads(last_message)
    print(last_message)
    assert len(last_message) == 4
    last_message = last_message[3]
    assert "hours" in last_message["_source"]["attachments"][0]["filename"]
