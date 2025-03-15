""" Tests for slack_processor module """
import json
from pprint import pprint

import elasticsearch
import helpers.s3
import pytest
import settings
import slack_parse.download_api.slack_api_downloader
import slack_parse.process.slack_processor

CLIENT_NAME = "ips"
# INDEX_NAME = "ips_data_slack"  # 'slack-parse-v1-000001'
# INDEX_NAME = "slack-parse-v1-000001"  # .get, .delete only support one underlying index
INDEX_NAME_2021_02 = "slack-parse-v1-2021-02"  # .get, .delete only support one underlying index

sample_event = {
    "channels": None,
    "date_y_m_d": "2020-12-22",
    "client_name": "ips",
    "messages_s3_paths": [
        "dev.todo.slack/2020-12-22/json-slack/messages/C01FHG8T7J5__slack-ingest/2020-12-22.json",
        "dev.todo.slack/2020-12-22/json-slack/messages/G01FQMA8UVA__mpdm-anthony--james--mike-1/2020-12-22.json",
        "dev.todo.slack/2020-12-22/json-slack/messages/DPE3CD7CY/2020-12-22.json",
    ],
    "users": None,
}


def test_get_messages_for_date():
    date_y_m_d = "2020-12-22"
    paths = helpers.s3.get_messages_for_date_from_archive(CLIENT_NAME, date_y_m_d)
    pprint(paths)
    assert len(paths) == 3


def test_get_channel_id_and_name_from_msg_key():
    msg_key = "dev.todo.slack/2020-12-22/json-slack/messages/C01FHG8T7J5__slack-ingest/2020-12-22.json"
    channel_name = slack_parse.process.slack_processor._get_channel_name_from_msg_key(msg_key)
    channel_id = slack_parse.process.slack_processor._get_channel_id_from_msg_key(msg_key)
    channel_label = slack_parse.process.slack_processor._get_channel_label_from_msg_key(msg_key)
    assert channel_name == "slack-ingest"
    assert channel_id == "C01FHG8T7J5"
    assert channel_label == "C01FHG8T7J5__slack-ingest"


def test_slack_processor_missing_arguments():
    with pytest.raises(Exception) as e_info:
        _ = slack_parse.process.slack_processor.SlackProcessor(client_name=CLIENT_NAME)
    assert "missing" in str(e_info.value)
    assert "argument" in str(e_info.value)


def test_slack_processor():
    sp = slack_parse.process.slack_processor.SlackProcessor(client_name=CLIENT_NAME, date_y_m_d="2020-12-22")
    assert sp is not None
    print(sp)
    assert "SlackProcessor" in str(sp)


def test_slack_processor_from_event():
    # Download data first
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    data = sd.download_all_data("2020-12-22")
    print(data)
    print(sample_event)
    assert sorted(data["messages_s3_paths"]) == sorted(
        sample_event["messages_s3_paths"]
    )  # altho channels/users might be populated if they are ever cleared

    # Process downloaded data
    p = slack_parse.process.slack_processor.process_slack_from_lambda_event(event=sample_event)
    assert p["ok"] is True
    assert p["num_messages_processed"] == 5
    assert p["client_name"] == CLIENT_NAME

    # Confirm cleaned up _todo folder
    s3_key = "dev.todo.slack/2020-12-22/json-slack/messages/DPE3CD7CY/2020-12-22.json"
    s3 = helpers.s3.S3(CLIENT_NAME, None)
    with pytest.raises(Exception) as e_info:
        s3.get(s3_key)
    assert "NoSuchKey" in str(e_info.value)

    # Confirm archived and processed both contain processed and raw slack files
    archived_raw_s3_key = "dev.archived.slack/2020-12-22/json-slack/messages/DPE3CD7CY/2020-12-22.json"
    assert s3.get(archived_raw_s3_key) is not None
    archived_processed_s3_key = "dev.archived.slack/2020-12-22/json-processed/messages/DPE3CD7CY/2020-12-22.json"
    assert s3.get(archived_processed_s3_key) is not None

    processed_raw_s3_key = "dev.processed.slack/2020-12-22/json-slack/messages/DPE3CD7CY/2020-12-22.json"
    assert s3.get(processed_raw_s3_key) is not None
    processed_processed_s3_key = "dev.processed.slack/2020-12-22/json-processed/messages/DPE3CD7CY/2020-12-22.json"
    assert s3.get(processed_processed_s3_key) is not None


def test_get_closest_metadata():
    date_y_m_d = "2020-12-16"  # should return like 20 something
    channels, users, is_future = helpers.s3.get_closest_metadata(CLIENT_NAME, date_y_m_d)
    assert users is not None
    assert channels is not None
    assert is_future is True


def test_slack_processor_from_yesterday():
    # Download data first
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    data = sd.download_all_data()

    # Process downloaded data
    p = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)
    assert p["ok"] is True
    assert p["num_messages_processed"] > 0  # always has slack daily export message
    # Confirm cleaned up _todo folder
    """
    s3_key='dev.todo.slack/2020-12-22/json-slack/messages/DPE3CD7CY/2020-12-22.json'
    s3 = helpers.s3.S3(CLIENT_NAME, None)
    with pytest.raises(Exception) as e_info:
        s3.get(s3_key)
        """


def test_slack_processor_from_archive():
    s3 = helpers.s3.S3(CLIENT_NAME, "2021-01-06")
    processed_raw_json_s3_path = "dev.processed.slack/2021-01-06/json-slack/messages/C01FHG8T7J5__slack-ingest/2021-01-06.json"
    s3.delete_file(processed_raw_json_s3_path)
    processed_s3_path = "dev.processed.slack/2021-01-06/json-processed/messages/C01FHG8T7J5__slack-ingest/2021-01-06__0-6.json"
    s3.delete_file(processed_s3_path)
    processed_attachment_path = "dev.processed.slack/2021-01-06/attachments/F01JT4DCVMW.tgz"
    processed_attachment_path = "dev.processed.slack/2021-01-06/attachments/F01JT4DCVMW.zip"
    s3.delete_file(processed_attachment_path)
    sp = slack_parse.process.slack_processor.SlackProcessor(CLIENT_NAME, "2021-01-06")
    sp.process()
    raw = s3.get(processed_raw_json_s3_path)
    assert raw is not None
    a = s3.get(processed_s3_path)
    assert a is not None
    p = json.loads(a)
    attachment_doc = p[6]
    assert "Yadda" in attachment_doc["_source"]["attachments"][0]["content"]
    print("\n\n\n\n from archive \n\n")
    pprint(p)

    attachment = s3.get(processed_attachment_path)
    assert attachment is not None


def test_slack_processor_for_private_chat():
    # Download data first
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    data = sd.download_all_data("2020-11-20")
    print(data)

    # Process downloaded data
    p = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)
    assert p["ok"] is True
    assert p["num_messages_processed"] > 0  # always has slack daily export message


def test_slack_processor_for_a_certain_date_once():
    ELASTIC_DOC_ID = "ips-C01FHG8T7J5-210205-5"
    es = get_es_instance()
    try:
        es.delete(index=INDEX_NAME_2021_02, id=ELASTIC_DOC_ID)
    except elasticsearch.exceptions.NotFoundError as e:
        print(e)

    # Download data first
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    data = sd.download_all_data("2021-02-05")
    print(data)

    # Process downloaded data
    p = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)
    assert p["ok"] is True
    assert p["num_messages_processed"] > 0  # always has slack daily export message
    doc = es.get(index=INDEX_NAME_2021_02, id=ELASTIC_DOC_ID)
    assert doc["_source"]["body"] == "reply in thread 16"
    assert doc["_source"]["body_detail"]["body_sentiment"]["neu"] == 1


def get_es_instance() -> elasticsearch.Elasticsearch:
    # stage = "dev"
    # ES_HOST = dict()
    # ES_PASSWORD = dict()

    # ssm = boto3.client("ssm")
    # ES_HOST[stage] = ssm.get_parameter(Name=f'/fingerprint/elastic/{stage}/ES_HOST')['Parameter']['Value']
    # ES_PASSWORD[stage] = \
    # ssm.get_parameter(Name=f'/fingerprint/elastic/{stage}/ES_PASSWORD', WithDecryption=True)['Parameter'][
    #    'Value']

    # # Get direct from AWS Parameter Store
    # ES_HOST[stage] = ssm.get_parameter(Name=f'/elastic_cluster/{stage}')['Parameter']['Value']
    # ES_USER[stage] = ssm.get_parameter(Name=f'/elastic_app/{stage}/slack/user')['Parameter']['Value']
    # ES_PASSWORD[stage] = ssm.get_parameter(Name=f'/elastic_app/{stage}/slack/password', WithDecryption=True)['Parameter']['Value']

    # es_host = ES_HOST[stage]
    # es_user = ES_USER[stage]
    # es_password = ES_PASSWORD[stage]

    es_host = settings.ES_HOST
    es_user = settings.ES_USER
    es_password = settings.ES_PASSWORD

    """
    connections.create_connection(
        alias='default',
        hosts=[es_host],
        http_auth=(es_user, es_password),
        scheme="https",
        timeout= 60,
        port=9243
    """

    es = elasticsearch.Elasticsearch(
        [es_host],
        http_auth=(es_user, es_password),
        scheme="https",
        port=443,
    )
    return es


"""
def test_slack_processor_for_a_certain_date_once():
    # Download data first
    sd = slack_parse.slack_data.SlackData(CLIENT_NAME)
    data = sd.download_all_data('2021-02-05')
    print(data)

    # Process downloaded data
    p = slack_parse.slack_processor.process_slack_from_lambda_event(data)
    assert(p['ok'] == True)
    assert(p['num_messages_processed'] > 0)  # always has slack daily export message
"""
