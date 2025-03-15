import elasticsearch
import settings
import slack_parse.download_api.slack_api_downloader
import slack_parse.process.slack_processor

CLIENT_NAME = "ips"
# INDEX_NAME = "ips_data_slack"  # 'slack-parse-v1-000001'
# INDEX_NAME = (
#     "slack-parse-v1-000001"  # Aliases only support get for one underlying index
# )
INDEX_NAME_2021_02 = "slack-parse-v1-2021-02"  # Aliases only support get for one underlying index


def get_es_instance() -> elasticsearch.Elasticsearch:
    # stage = 'dev'
    # ES_HOST = dict()
    # ES_PASSWORD = dict()

    # ssm = boto3.client("ssm")
    # ES_HOST[stage] = ssm.get_parameter(Name=f'/fingerprint/elastic/{stage}/ES_HOST')['Parameter']['Value']
    # ES_PASSWORD[stage] = \
    # ssm.get_parameter(Name=f'/fingerprint/elastic/{stage}/ES_PASSWORD', WithDecryption=True)['Parameter'][
    #    'Value']

    # es_host = ES_HOST[stage]
    # es_password = ES_PASSWORD[stage]

    es_host = settings.ES_HOST
    es_user = settings.ES_USER
    es_password = settings.ES_PASSWORD

    """
    connections.create_connection(
        alias='default',
        hosts=[es_host],
        http_auth=('elastic', es_password),
        scheme="https",
        timeout= 60,
        port=9243
    )
    """
    es = elasticsearch.Elasticsearch(
        [es_host],
        http_auth=(es_user, es_password),
        scheme="https",
        port=443,
    )
    return es


def test_dl_process_in_es():
    date_y_m_d = "2021-02-25"
    # s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    # Delete doc from ES to see if it is re-created
    ID_ATTACH = "ips-CP7KZPEKT-210225-4"
    ID = "ips-CP7KZPEKT-210225-7"
    es = get_es_instance()
    # res = es.get(index=INDEX_NAME_2021_02, id=ID)
    try:
        res = es.delete(index=INDEX_NAME_2021_02, id=ID_ATTACH)
        res = es.delete(index=INDEX_NAME_2021_02, id=ID)
    except elasticsearch.exceptions.NotFoundError as e:
        print(e)
    try:
        res = es.delete(index=INDEX_NAME_2021_02, id=ID)
    except elasticsearch.exceptions.NotFoundError as e:
        print(e)
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    data = sd.download_all_data(date_y_m_d)
    print(data)
    out = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)
    print(out)
    attach_res = es.get(index=INDEX_NAME_2021_02, id=ID_ATTACH)
    print(attach_res)
    a_source = attach_res["_source"]
    assert a_source["attachments"][0]["filename"] == "Test document to upload into slack.docx"
    assert "Yadda" in a_source["attachments"][0]["content"]
    assert a_source["attachments"][0]["tar_file_location"] == "dev.processed.slack/2021-02-25/attachments/F01PK6JAZHS.zip"
    assert a_source["to_detail"][0]["fullname"] == "Brielle Hewitt"
    assert a_source["from_"] == "anthony <None>"
    assert a_source["from_detail"]["fullname"] == "anthony"
    assert a_source["item_id"]["es_id"] == "ips-CP7KZPEKT-210225-4"

    res = es.get(index=INDEX_NAME_2021_02, id=ID)
    print(res)
    source = res["_source"]
    assert source["body"] == "That's it!"
    assert source["body_detail"]["body_sentiment"]["neu"] == 1
    assert source["to_detail"][0]["fullname"] == "Brielle Hewitt"
    assert source["from_"] == "anthony <None>"
    assert source["from_detail"]["fullname"] == "anthony"
    assert a_source["item_id"]["es_id"] == "ips-CP7KZPEKT-210225-4"
