import json

import helpers.s3
import slack_parse.download_api.slack_api_downloader
import slack_parse.process.slack_processor

CLIENT_NAME = "ips"


def test_shared_channels():
    date_y_m_d = "2021-03-05"
    processed_key = "dev.processed.slack/2021-03-05/json-processed/messages/C01QGS0EQ4C__test-shared-channel/2021-03-05__0-4.json"  # FPS slack connect subscription expired, caused removal of messages, was 0-5.json messages before
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    s3.delete_file(processed_key)
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    data = sd.download_all_data(date_y_m_d)
    p = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)
    print(p)
    messages = json.loads(s3.get(processed_key))
    print(messages)
    print(messages[2]["_source"])
    assert messages[2]["_source"]["body"] == "chat from IPS on test-shared-channel"
    assert messages[2]["_source"]["to"][0] == "anthony-fps <None>"
    print(messages[3])
    assert messages[3]["_source"]["body"] == "chat from fps with attachment"
