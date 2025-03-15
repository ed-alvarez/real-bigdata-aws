import json

import settings
import slack_parse.download_api.slack_api_downloader
import slack_parse.process.slack_processor

CLIENT_NAME = "ips"
TESTING_ES_SIZE_LIMIT = 0.020  # remember to cast env variables to float


def test_slack_processor_for_es_batch_size(monkeypatch):
    # date_y_m_d = '2020-11-20'
    date_y_m_d = "2021-02-11"

    cc_file_s3_key = "dev.processed.slack/2021-02-11/json-processed/messages/C01FHG8T7J5__slack-ingest/2021-02-11__19-20.json"

    # Set environment variable before importing
    # os.environ['ES_UPLOAD_MAX_SIZE_MB'] = TESTING_ES_SIZE_LIMIT
    # Use monkeypatch which will reset the env variable after the test rather
    # than keep it for other tests
    # monkeypatch.setenv('ES_UPLOAD_MAX_SIZE_MB', TESTING_ES_SIZE_LIMIT) module isn't re imported so it doesn't pick up env variable changes later on in tests, monkey patch the setting instead.
    monkeypatch.setattr(settings, "ES_UPLOAD_MAX_SIZE_MB", TESTING_ES_SIZE_LIMIT)

    # Remove last file of batch to make sure that it is created
    import helpers.s3

    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    s3.delete_file(cc_file_s3_key)

    # Download data first
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    data = sd.download_all_data(date_y_m_d)
    print(data)

    # Process downloaded data
    p = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)
    assert p["ok"] is True
    assert p["num_messages_processed"] > 0  # always has slack daily export message
    cc_message_file = s3.get(cc_file_s3_key)
    cc_message_file = json.loads(cc_message_file)
    print(cc_message_file)
    assert len(cc_message_file) == 2
    cc_message = cc_message_file[0]
    assert "cc" in cc_message["_source"]["body"]
    cc_attachment = cc_message_file[1]
    assert "slack_ingest" in cc_attachment["_source"]["attachments"][0]["filename"]
