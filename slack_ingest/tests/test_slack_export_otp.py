import json

import boto3
import botocore
import elasticsearch
import helpers.s3
import pytest
import settings
import slack_parse.download_export.slack_export_downloader as sed
import slack_parse.process.slack_processor

CLIENT_NAME = "ips"
INDEX_NAME = "ips_data_slack"  # 'slack-parse-v1-000001'
INDEX_NAME = "slack-parse-v1-000001"
INDEX_NAME = "slack-parse-v1-2021-03"


def get_es_instance() -> elasticsearch.Elasticsearch:
    # stage = 'dev'
    # ES_HOST = dict()
    # ES_PASSWORD = dict()

    # ssm = boto3.client('ssm')
    # ES_HOST[stage] = ssm.get_parameter(Name=f'/fingerprint/elastic/{stage}/ES_HOST')['Parameter']['Value']
    # ES_PASSWORD[stage] = \
    # ssm.get_parameter(Name=f'/fingerprint/elastic/{stage}/ES_PASSWORD', WithDecryption=True)['Parameter'][
    #     'Value']

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


def test_slack_export_otp_free():
    CLIENT_NAME = "fps-dzs5812-otp"
    date_y_m_d = "2011-07-24"
    # s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    with pytest.raises(sed.NoDataFoundException) as e_info:
        _ = sed.download_from_lambda_event({"client_name": CLIENT_NAME, "date_y_m_d": date_y_m_d})
    print(e_info)
    # KeyError: "There is no item named 'dms.json' in the archive
    assert """Could not find requested date in exports""" in str(e_info.value)
    # print(data) won't be available
    return


def test_slack_export_otp():
    CLIENT_NAME = "ips"
    # date_y_m_d = (datetime.now() - timedelta(2)).strftime("%Y-%m-%d")
    date_y_m_d = "2011-07-24"  # won't be found
    # s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    with pytest.raises(sed.NoDataFoundException) as e_info:
        _ = sed.download_from_lambda_event({"client_name": CLIENT_NAME, "date_y_m_d": date_y_m_d})
    print(e_info)
    # KeyError: "There is no item named 'dms.json' in the archive Now we support public channel only exports
    # assert """There is no item named 'dms.json' in the archive""" in str(e_info.value)
    assert """Could not find requested date in exports""" in str(e_info.value)
    # print(data) won't be available
    return


def test_slack_export_otp_eg():
    CLIENT_NAME = "ips-eg-otp"
    date_y_m_d = "2021-07-24"
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)

    """
    # DELETE TODOS TODO delete processed
    tom_message_direct_message = (
        "dev.todo.slack/2021-03-18/json-slack/messages/D01FGAZFL65/2021-03-18.json"
    )
    s3.delete_file(tom_message_direct_message)
    s3.delete_file(tom_message_direct_message.replace("dev.todo", "dev.processed"))
    s3.delete_file(
        "dev.processed.slack/2021-03-18/json-processed/messages/D01FGAZFL65/2021-03-18__0-1.json"
    )
    """

    # Delete all attachments
    attachments = []
    for att in attachments:
        s3.delete_file(att)

    # data = sed.download(CLIENT_NAME, date_y_m_d)
    data = sed.download_from_lambda_event({"client_name": CLIENT_NAME, "date_y_m_d": date_y_m_d})
    print(data)
    return

    msg_counts = (
        1,
        3,
        4,
        1,
    )  # Slack Connect trial expired 6)
    for msg, msg_count in zip(
        [
            # tom_message_direct_message,
            # priv_channel,
            # shared_channel,
            # normal_channel,
            # slack connect trial expired direct_message_with_slack_connect,
        ],
        msg_counts,
    ):
        todo_json = json.loads(s3.get(msg))
        assert todo_json is not None
        print(todo_json)
        print(len(todo_json))
        assert len(todo_json) == msg_count

    s3.delete_file("dev.processed.slack/2021-03-18/json-slack/messages/G01QGS2FY1J__test-private-channel/2021-03-18.json")
    s3.delete_file("dev.processed.slack/2021-03-18/json-processed/messages/G01QGS2FY1J__test-private-channel/2021-03-18__0-12.json")

    sp_res = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)
    print(sp_res)
    # {'ok': True, 'continue': False, 'num_messages_processed': 34, 'client_name': 'ips', 'date_y_m_d': '2021-03-17'}
    assert sp_res["ok"] is True
    assert sp_res["continue"] is False
    assert sp_res["num_messages_processed"] == 14  # Slack Connect trial expired 21
    assert sp_res["client_name"] == CLIENT_NAME
    assert sp_res["date_y_m_d"] == date_y_m_d

    from pprint import pprint

    """ Slack Connect Trial Expired
    # Test slack connect dm
    slack_connect_dms = json.loads(
        s3.get(
            "dev.processed.slack/2021-03-18/json-processed/messages/D01QANDH718/2021-03-18__0-6.json"
        )
    )


    # pprint(slack_connect_dms)
    assert slack_connect_dms[3]["_source"]["body"] == "Hi anthony-ips"
    assert slack_connect_dms[3]["_source"]["from_"] == "anthony-fps <None>"
    ID = "ips-D01QANDH718-210318-3"
    es = get_es_instance()
    res = es.get(index=INDEX_NAME, id=ID)
    # print(res)
    source = res["_source"]
    assert source["body"] == "Hi anthony-ips"
    assert source["from_"] == "anthony-fps <None>"
    ID = "ips-D01QANDH718-210318-6"
    es = get_es_instance()
    res = es.get(index=INDEX_NAME, id=ID)
    source = res["_source"]
    assert "Yadda" in source["attachments"][0]["content"]
    assert source["from_"] == "anthony-fps <None>"
    assert source["to"][0] == "anthony <anthony@ip-sentinel.com>"
    assert len(source["to"]) == 1  # Ensure from user is removed
    """

    # Test dm with Tom
    dm_with_tom = json.loads(s3.get("dev.processed.slack/2021-03-18/json-processed/messages/D01FGAZFL65/2021-03-18__0-1.json"))
    pprint(dm_with_tom)
    assert dm_with_tom[0]["_source"]["body"].startswith("Hi please ignore this message, I need to test the scenario")
    assert dm_with_tom[0]["_source"]["to"] == ["Tom Vavrechka <tom@ip-sentinel.com>"]
    import io
    import zipfile

    bytes = io.BytesIO(s3.get(dm_with_tom[1]["_source"]["attachments"][0]["tar_file_location"]))
    with zipfile.ZipFile(bytes) as zf:
        assert len(zf.namelist()) == 1
        assert "docx" in zf.namelist()[0]
        assert "document" in zf.namelist()[0]
        word_docx = io.BytesIO(zf.read(zf.namelist()[0]))
        with zipfile.ZipFile(word_docx) as wd:
            xml = wd.read("word/document.xml")
            assert b"Some more words, trading, groups and computers." in xml

    # Test private channel
    priv_channel = json.loads(
        s3.get("dev.processed.slack/2021-03-18/json-processed/messages/G01QGS2FY1J__test-private-channel/2021-03-18__0-3.json")
    )
    pprint(priv_channel)
    assert "private" in priv_channel[0]["_source"]["body"]
    assert priv_channel[0]["_source"]["to"] == ["anthony <anthony@ip-sentinel.com>"]
    assert priv_channel[0]["_source"]["from_"] == "anthony <anthony@ip-sentinel.com>"
    ID = "ips-G01QGS2FY1J-210318-1"
    es = get_es_instance()
    res = es.get(index=INDEX_NAME, id=ID)
    source = res["_source"]
    assert source["body"] == "That 6MB pdf seemed to really slow things down"

    # Shared channel
    shared_channel = json.loads(
        s3.get("dev.processed.slack/2021-03-18/json-processed/messages/C01QGS0EQ4C__test-shared-channel/2021-03-18__0-5.json")
    )
    pprint(shared_channel)
    assert shared_channel[1]["_source"]["body"] == "messages in a shared channel from fps"
    assert shared_channel[1]["_source"]["from_"] == "anthony-fps <None>"
    ATTACH_ID = "ips-C01QGS0EQ4C-210318-5"
    es = get_es_instance()
    res = es.get(index=INDEX_NAME, id=ATTACH_ID)
    source = res["_source"]
    assert "trading, groups and computers" in source["attachments"][0]["content"]

    # Normal channel, slack-ingest
    normal_channel = json.loads(
        s3.get("dev.processed.slack/2021-03-18/json-processed/messages/C01FHG8T7J5__slack-ingest/2021-03-18__0-0.json")
    )
    pprint(normal_channel)
    assert normal_channel[0]["_source"]["body"] == "And messages in a normal channel"
    ID = ("ips-C01FHG8T7J5-210318-0",)
    es = get_es_instance()
    res = es.get(index=INDEX_NAME, id=ID)
    source = res["_source"]
    assert source["body"] == "And messages in a normal channel"

    # Shared channel
    shared_channel = json.loads(
        s3.get("dev.processed.slack/2021-03-18/json-processed/messages/C01QGS0EQ4C__test-shared-channel/2021-03-18__0-5.json")
    )
    pprint(shared_channel)

    normal_channel = json.loads(
        s3.get("dev.processed.slack/2021-03-18/json-processed/messages/C01FHG8T7J5__slack-ingest/2021-03-18__0-0.json")
    )
    pprint(normal_channel)
    ID = ("ips-C01FHG8T7J5-210318-0",)
    assert normal_channel[0]["_source"]["body"] == "And messages in a normal channel"

    # Check attachments exist
    s3_client = boto3.client("s3")

    def s3_file_exists(s3_client, bucket, key):
        try:
            return s3_client.head_object(Bucket=bucket, Key=key)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print(f"{key} doesn't exist")
                raise f"{key} doesn't exist"
            else:
                # Something else has gone wrong.
                raise

    # Check attachments exist
    for att in attachments:
        assert s3_file_exists(s3_client, f"{CLIENT_NAME}.ips", att)
