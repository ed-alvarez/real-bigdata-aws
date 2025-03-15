import json

import settings
import slack_parse.download_api.slack_api_downloader
import slack_parse.process.slack_processor

CLIENT_NAME = "ips"
LAMBDA_MIN_TIME_REQUIRED_SECS = 90  # str(90) # string if env variable. have to recast it.


def test_slack_processor_for_lambda_timeout(monkeypatch):
    # date_y_m_d = '2020-11-20'
    date_y_m_d = "2021-02-05"

    first_file_s3_key = "dev.processed.slack/2021-02-05/json-processed/messages/C01FHG8T7J5__slack-ingest/2021-02-05__0-0.json"

    def monkey_patch_get_remaining_time_secs(self):
        return 10

    # Set environment variable before importing
    # don't do this, patch the variable itself os.environ['LAMBDA_MIN_TIME_REQUIRED_SECS'] = LAMBDA_MIN_TIME_REQUIRED_SECS
    monkeypatch.setattr(settings, "LAMBDA_MIN_TIME_REQUIRED_SECS", LAMBDA_MIN_TIME_REQUIRED_SECS)
    # don't do this, use monkeypatch so that the method is only replaced
    # for the lifetime of the test
    # slack_parse.slack_processor.SlackProcessor.get_remaining_time_secs = monkey_patch_get_remaining_time_secs
    monkeypatch.setattr(
        slack_parse.process.slack_processor.SlackProcessor,
        "get_remaining_time_secs",
        monkey_patch_get_remaining_time_secs,
    )

    # Remove last file of batch to make sure that it is created
    import helpers.s3

    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    s3.delete_file(first_file_s3_key)

    # Download data first
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    data = sd.download_all_data(date_y_m_d)
    print(data)

    # Process downloaded data
    p = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)

    assert p["ok"] is True
    assert p["num_messages_processed"] > 0  # always has slack daily export message
    first_message_file = s3.get(first_file_s3_key)
    first_message_file = json.loads(first_message_file)
    print(first_message_file)
    assert len(first_message_file) == 1
    first_message = first_message_file[0]
    assert "11" in first_message["_source"]["body"]

    print(p)
    assert "continue" in p and p["continue"] is True
    assert p["continue_from_channel_id"] == "C01FHG8T7J5"
    assert p["continue_from_msg_num"] == 1
    assert p["continue_from_item_num"] == 1


def test_slack_processor_for_lambda_timeout_continue(monkeypatch):
    # date_y_m_d = '2020-11-20'
    # date_y_m_d = '2021-02-11'
    date_y_m_d = "2021-02-15"

    first_file_s3_key = "dev.processed.slack/2021-02-15/json-processed/messages/C01FHG8T7J5__slack-ingest/2021-02-15__0-0.json"
    first_attachment_s3_key = "dev.processed.slack/2021-02-15/json-processed/messages/C01FHG8T7J5__slack-ingest/2021-02-15__2-3.json"
    second_att_s3_key = "dev.processed.slack/2021-02-15/json-processed/messages/C01FHG8T7J5__slack-ingest/2021-02-15__7-10.json"

    def monkey_patch_get_remaining_time_secs(self):
        return 10

    # Set environment variable before importing
    # don't do this, change the variable itself. os.environ['LAMBDA_MIN_TIME_REQUIRED_SECS'] = LAMBDA_MIN_TIME_REQUIRED_SECS
    monkeypatch.setattr(settings, "LAMBDA_MIN_TIME_REQUIRED_SECS", LAMBDA_MIN_TIME_REQUIRED_SECS)
    import slack_parse.download_api.slack_api_downloader
    import slack_parse.process.slack_processor

    # don't do this, use monkeypatch so that the method is only replaced
    # for the lifetime of the test
    # slack_parse.slack_processor.SlackProcessor.get_remaining_time_secs = monkey_patch_get_remaining_time_secs
    monkeypatch.setattr(
        slack_parse.process.slack_processor.SlackProcessor,
        "get_remaining_time_secs",
        monkey_patch_get_remaining_time_secs,
    )

    # Remove last file of batch to make sure that it is created
    import helpers.s3

    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    s3.delete_file(first_file_s3_key)
    s3.delete_file(first_attachment_s3_key)
    s3.delete_file(second_att_s3_key)

    # Download data first
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    data = sd.download_all_data(date_y_m_d)
    print(data)

    # Process downloaded data
    p = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)

    assert p["ok"] is True
    assert p["num_messages_processed"] > 0  # always has slack daily export message
    first_message_file = s3.get(first_file_s3_key)
    first_message_file = json.loads(first_message_file)
    print(first_message_file)
    assert len(first_message_file) == 1
    first_message = first_message_file[0]
    assert "13" in first_message["_source"]["body"]

    print(p)
    assert "continue" in p and p["continue"] is True
    assert p["continue_from_channel_id"] == "C01FHG8T7J5"
    assert p["continue_from_msg_num"] == 1
    assert p["continue_from_item_num"] == 1

    # Continue
    i = 0
    while True:
        p = slack_parse.process.slack_processor.process_slack_from_lambda_event(p)
        print(p)
        print(i)
        if i < 8:
            assert "continue" in p and p["continue"] is True
        else:
            assert p["ok"] is True and p["continue"] is False
            break
        i += 1

    first_attachment_msgs = json.loads(s3.get(first_attachment_s3_key))
    assert len(first_attachment_msgs) == 2
    assert first_attachment_msgs[0]["_source"]["body"] == "15 in thread with attachment"
    assert first_attachment_msgs[1]["_source"]["attachments"][0]["filename"] == "TASK LIST SLACK INGEST.docx"

    second_att_msgs = json.loads(s3.get(second_att_s3_key))
    assert len(second_att_msgs) == 4
    assert "18 in channel with three" in second_att_msgs[0]["_source"]["body"]
    assert second_att_msgs[1]["_source"]["attachments"][0]["filename"] == "Test document for word.docx"
    assert second_att_msgs[2]["_source"]["attachments"][0]["filename"] == "Test document to upload into slack.docx"
    assert "talk-for-14-hours" in second_att_msgs[3]["_source"]["attachments"][0]["filename"]


def tes_slack_processor_for_lambda_timeout_continue_longer(monkeypatch):
    # This is a longer test, feel free to run it though!
    # date_y_m_d = '2020-11-20'
    date_y_m_d = "2021-02-11"
    # date_y_m_d = '2021-02-15'

    first_file_s3_key = "dev.processed.slack/2021-02-11/json-processed/messages/C01FHG8T7J5__slack-ingest/2021-02-11__0-0.json"
    first_attachment_s3_key = "dev.processed.slack/2021-02-11/json-processed/messages/C01FHG8T7J5__slack-ingest/2021-02-11__3-4.json"
    second_att_s3_key = "dev.processed.slack/2021-02-11/json-processed/messages/C01FHG8T7J5__slack-ingest/2021-02-11__12-14.json"

    def monkey_patch_get_remaining_time_secs(self):
        return 10

    # Set environment variable before importing
    # don't do this, change the variable itself. os.environ['LAMBDA_MIN_TIME_REQUIRED_SECS'] = LAMBDA_MIN_TIME_REQUIRED_SECS
    monkeypatch.setattr(settings, "LAMBDA_MIN_TIME_REQUIRED_SECS", LAMBDA_MIN_TIME_REQUIRED_SECS)
    import slack_parse.download_api.slack_api_downloader
    import slack_parse.process.slack_processor

    # don't do this, use monkeypatch so that the method is only replaced
    # for the lifetime of the test
    # slack_parse.slack_processor.SlackProcessor.get_remaining_time_secs = monkey_patch_get_remaining_time_secs
    monkeypatch.setattr(
        slack_parse.process.slack_processor.SlackProcessor,
        "get_remaining_time_secs",
        monkey_patch_get_remaining_time_secs,
    )

    # Remove last file of batch to make sure that it is created
    import helpers.s3

    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    s3.delete_file(first_file_s3_key)
    s3.delete_file(first_attachment_s3_key)
    s3.delete_file(second_att_s3_key)

    # Download data first
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    data = sd.download_all_data(date_y_m_d)
    print(data)

    # Process downloaded data
    p = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)

    assert p["ok"] is True
    assert p["num_messages_processed"] > 0  # always has slack daily export message
    first_message_file = s3.get(first_file_s3_key)
    first_message_file = json.loads(first_message_file)
    print(first_message_file)
    assert len(first_message_file) == 1
    first_message = first_message_file[0]
    assert "mm" in first_message["_source"]["body"]

    print(p)
    assert "continue" in p and p["continue"] is True
    assert p["continue_from_channel_id"] == "C01FHG8T7J5"
    assert p["continue_from_msg_num"] == 1
    assert p["continue_from_item_num"] == 1

    # Continue
    i = 0
    while True:
        p = slack_parse.process.slack_processor.process_slack_from_lambda_event(p)
        print(p)
        print(i)
        if i < 24:
            assert "continue" in p and p["continue"] is True
        else:
            assert p["ok"] is True and p["continue"] is False
            break
        i += 1

    first_attachment_msgs = json.loads(s3.get(first_attachment_s3_key))
    assert len(first_attachment_msgs) == 2
    assert first_attachment_msgs[0]["_source"]["body"] == "pp"
    assert first_attachment_msgs[1]["_source"]["attachments"][0]["filename"] == "task_list_slack_ingest.docx"

    second_att_msgs = json.loads(s3.get(second_att_s3_key))
    assert len(second_att_msgs) == 3
    assert second_att_msgs[0]["_source"]["body"] == "xx"
    assert second_att_msgs[1]["_source"]["attachments"][0]["filename"] == "test_document_for_word.docx"
    assert second_att_msgs[2]["_source"]["attachments"][0]["filename"] == "test_document_to_upload_into_slack.docx"
