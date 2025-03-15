import json
from pprint import pprint

import boto3
import botocore
import elasticsearch
import helpers.s3
import pytest
import settings
import slack_parse.download_export.slack_export_downloader as sed
import slack_parse.process.slack_processor

CLIENT_NAME = "fps"
# INDEX_NAME = "ips_data_slack"  # 'slack-parse-v1-000001'
INDEX_NAME = "slack-parse-v1-000001"  # .get only supports one underlying index for aliases anyway
INDEX_NAME = "slack-parse-v1-2021-05"  # .get only supports one underlying index for aliases anyway


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


def test_slack_export_ent_grid_mpim():
    print("testing mpim")
    date_y_m_d = "2021-05-20"
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)

    # Delete processed file
    mpim_file = "dev.processed.slack/2021-05-20/json-processed/messages/C022C955X0W__mpdm-anthony--anthony679--slack-sandbox-1/2021-05-20__0-5.json"
    normal_channel_file = "dev.processed.slack/2021-05-20/json-processed/messages/C022EFUDTK5__slack-discovery/2021-05-20__0-8.json"
    shared_private_channel_file = (
        "dev.processed.slack/2021-05-20/json-processed/messages/C022LEGLR52__slack-discovery-private/2021-05-20__0-7.json"
    )
    private_channel_file = "dev.processed.slack/2021-05-20/json-processed/messages/C022LGG144U__normal-private/2021-05-20__0-5.json"
    dm_file = "dev.processed.slack/2021-05-20/json-processed/messages/D022SUEAG1X/2021-05-20__0-0.json"

    s3.delete_file(mpim_file)
    s3.delete_file(normal_channel_file)
    s3.delete_file(shared_private_channel_file)
    s3.delete_file(private_channel_file)
    s3.delete_file(dm_file)

    data = sed.download_from_lambda_event({"client_name": CLIENT_NAME, "date_y_m_d": date_y_m_d})
    "dev.todo.slack/2021-05-20/json-slack/messages/C022C955X0W__mpdm-anthony--anthony679--slack-sandbox-1/2021-05-20.json"
    print(data)
    sp_res = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)
    print(sp_res)
    processed_msgs_for_mpdm = json.loads(s3.get(mpim_file))
    print(processed_msgs_for_mpdm[5])
    assert "Yadda" in processed_msgs_for_mpdm[5]["_source"]["attachments"][0]["content"]
    msgs_for_normal_channel = json.loads(s3.get(normal_channel_file))
    print(msgs_for_normal_channel[7])
    print(msgs_for_normal_channel[8])
    assert "attachment" in msgs_for_normal_channel[7]["_source"]["body"]
    assert "trading" in msgs_for_normal_channel[8]["_source"]["attachments"][0]["content"]
    msgs_for_shared_private_channel = json.loads(s3.get(shared_private_channel_file))
    assert "a" == msgs_for_shared_private_channel[5]["_source"]["body"]
    assert "c" == msgs_for_shared_private_channel[7]["_source"]["body"]

    msgs_for_private_channel = json.loads(s3.get(private_channel_file))
    print(msgs_for_private_channel[3])
    print(msgs_for_private_channel[5])
    assert "3" == msgs_for_private_channel[3]["_source"]["body"]
    assert "trading, groups and computers" in msgs_for_private_channel[5]["_source"]["attachments"][0]["content"]

    msgs_for_dm = json.loads(s3.get(dm_file))
    print(msgs_for_dm[0])
    assert "some private messages to ips" in msgs_for_dm[0]["_source"]["body"]


def test_slack_export_ent_grid():
    date_y_m_d = "2021-05-19"
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)

    # DELETE TODOS TODO delete processed
    direct_message = "dev.todo.slack/2021-05-19/json-slack/messages/D022SUEAG1X/2021-05-19.json"
    s3.delete_file(direct_message)
    s3.delete_file(direct_message.replace("dev.todo", "dev.processed"))
    s3.delete_file("dev.processed.slack/2021-05-19/json-processed/messages/D022SUEAG1X/2021-05-19__0-6.json")

    priv_channel = "dev.todo.slack/2021-05-19/json-slack/messages/C022LGG144U__normal-private/2021-05-19.json"
    s3.delete_file(priv_channel)
    s3.delete_file(priv_channel.replace("dev.todo", "dev.processed"))
    s3.delete_file("dev.processed.slack/2021-05-19/json-processed/messages/C022LGG144U__normal-private/2021-05-19__0-8.json")

    shared_channel = "dev.todo.slack/2021-05-19/json-slack/messages/C022LEGLR52__slack-discovery-private/2021-05-19.json"
    s3.delete_file(shared_channel)
    s3.delete_file(shared_channel.replace("dev.todo", "dev.processed"))
    s3.delete_file(
        "dev.processed.slack/2021-05-19/json-processed/messages/C022LEGLR52__slack-discovery-private/2021-05-19__0-5.json"  # Exports contents changed
    )

    normal_channel = "dev.todo.slack/2021-05-19/json-slack/messages/C022EFUDTK5__slack-discovery/2021-05-19.json"
    s3.delete_file(normal_channel)
    s3.delete_file(normal_channel.replace("dev.todo", "dev.processed"))
    s3.delete_file("dev.processed.slack/2021-05-19/json-processed/messages/C022EFUDTK5__slack-discovery/2021-05-19__0-16.json")

    # Delete all attachments
    attachments = [
        "dev.processed.slack/2021-05-19/attachments/F021ZJFKPDM.zip",
        "dev.processed.slack/2021-05-19/attachments/F0227JE3KP0.zip",
        "dev.processed.slack/2021-05-19/attachments/F022B9H8621.zip",
    ]
    for att in attachments:
        s3.delete_file(att)

    # data = sed.download(CLIENT_NAME, date_y_m_d)
    data = sed.download_from_lambda_event({"client_name": CLIENT_NAME, "date_y_m_d": date_y_m_d})
    print(data)
    channels = [
        direct_message,
        priv_channel,
        shared_channel,
        normal_channel,
    ]

    msg_counts = (7, 8, 7, 15)
    for msg, msg_count in zip(
        channels,
        msg_counts,
    ):
        todo_json = json.loads(s3.get(msg))
        assert todo_json is not None
        print(todo_json)
        print(len(todo_json))
        assert len(todo_json) == msg_count
    """

    s3.delete_file(
        "dev.processed.slack/2021-03-18/json-slack/messages/G01QGS2FY1J__test-private-channel/2021-03-18.json"
    )
    s3.delete_file(
        "dev.processed.slack/2021-03-18/json-processed/messages/G01QGS2FY1J__test-private-channel/2021-03-18__0-12.json"
    )
    """
    sp_res = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)
    print(sp_res)
    # {'ok': True, 'continue': False, 'num_messages_processed': 34, 'client_name': 'ips', 'date_y_m_d': '2021-03-17'}
    assert sp_res["ok"] is True
    assert sp_res["continue"] is False
    assert sp_res["num_messages_processed"] == 43  # got changed somehow 50
    assert sp_res["client_name"] == CLIENT_NAME
    assert sp_res["date_y_m_d"] == date_y_m_d

    """
    # Test slack connect dm
    slack_connect_dms = json.loads(
        s3.get(
            "dev.processed.slack/2021-03-18/json-processed/messages/D01QANDH718/2021-03-18__0-6.json"
        )
    )
    from pprint import pprint

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

    # Test dm between two non-owners
    dm = json.loads(s3.get("dev.processed.slack/2021-05-19/json-processed/messages/D022SUEAG1X/2021-05-19__0-6.json"))
    pprint(dm)
    assert dm[0]["_source"]["body"].startswith("Testing private direct messages")
    assert dm[2]["_source"]["body"] == "b"

    print(dm[0]["_source"]["to"])
    assert dm[0]["_source"]["to"] == ["Anthony Leung FPS <Anthony@fingerprint-supervision.com>"]

    """
    import zipfile
    import io

    bytes = io.BytesIO(
        s3.get(dm_with_tom[1]["_source"]["attachments"][0]["tar_file_location"])
    )
    with zipfile.ZipFile(bytes) as zf:
        assert len(zf.namelist()) == 1
        assert "docx" in zf.namelist()[0]
        assert "document" in zf.namelist()[0]
        word_docx = io.BytesIO(zf.read(zf.namelist()[0]))
        with zipfile.ZipFile(word_docx) as wd:
            xml = wd.read("word/document.xml")
            assert b"Some more words, trading, groups and computers." in xml
    """
    # Test private channel
    priv_channel = json.loads(
        s3.get("dev.processed.slack/2021-05-19/json-processed/messages/C022LGG144U__normal-private/2021-05-19__0-8.json")
    )
    pprint(priv_channel)
    assert "testing" in priv_channel[3]["_source"]["body"]
    print(priv_channel[0]["_source"]["to"])
    print(priv_channel[0]["_source"]["from_"])
    assert priv_channel[0]["_source"]["to"] == ["Anthony Leung IPS <anthony@ip-sentinel.com>"]
    assert priv_channel[0]["_source"]["from_"] == "Anthony Leung FPS <Anthony@fingerprint-supervision.com>"
    ID = "fps-C022LGG144U-210519-3"
    es = get_es_instance()
    res = es.get(index=INDEX_NAME, id=ID)
    source = res["_source"]
    assert source["body"] == "testing"
    ATTACH_ID = "fps-C022LGG144U-210519-8"
    es = get_es_instance()
    res = es.get(index=INDEX_NAME, id=ATTACH_ID)
    source = res["_source"]
    assert "Yadda" in source["attachments"][0]["content"]

    # Shared channel
    shared_channel = json.loads(
        s3.get(
            "dev.processed.slack/2021-05-19/json-processed/messages/C022LEGLR52__slack-discovery-private/2021-05-19__0-5.json"  # Export contents changed
        )
    )
    pprint(shared_channel)
    print(shared_channel[3]["_source"]["body"])
    print(shared_channel[3]["_source"]["from_"])
    assert (
        shared_channel[3]["_source"]["body"]
        == "Hello from Anthony Leung IPS"
        # "messages in a shared channel from fps"
    )
    assert shared_channel[3]["_source"]["from_"] == "Anthony Leung IPS <anthony@ip-sentinel.com>"
    """
    ATTACH_ID = "ips-C01QGS0EQ4C-210318-5"
    es = get_es_instance()
    res = es.get(index=INDEX_NAME, id=ATTACH_ID)
    source = res["_source"]
    assert "trading, groups and computers" in source["attachments"][0]["content"]
    """

    # Normal channel, slack-ingest
    normal_channel = json.loads(
        s3.get("dev.processed.slack/2021-05-19/json-processed/messages/C022EFUDTK5__slack-discovery/2021-05-19__0-16.json")
    )
    pprint(normal_channel)
    assert normal_channel[14]["_source"]["body"] == "normal file in channel"
    ID = ("fps-C022EFUDTK5-210519-14",)
    es = get_es_instance()
    res = es.get(index=INDEX_NAME, id=ID)
    source = res["_source"]
    assert source["body"] == "normal file in channel"

    # Check attachment from S3
    # 'dev.processed.slack/2021-05-19/attachments/F0227JE3KP0.zip'
    import io
    import zipfile

    bytes = io.BytesIO(s3.get(normal_channel[16]["_source"]["attachments"][0]["tar_file_location"]))
    with zipfile.ZipFile(bytes) as zf:
        assert len(zf.namelist()) == 1
        assert "docx" in zf.namelist()[0]
        assert "TASK LIST" in zf.namelist()[0]
        word_docx = io.BytesIO(zf.read(zf.namelist()[0]))
        with zipfile.ZipFile(word_docx) as wd:
            xml = wd.read("word/document.xml")
            assert b"Lambda to lambda" in xml

    """
    # Shared channel
    shared_channel = json.loads(
        s3.get(
            "dev.processed.slack/2021-03-18/json-processed/messages/C01QGS0EQ4C__test-shared-channel/2021-03-18__0-5.json"
        )
    )
    pprint(shared_channel)

    normal_channel = json.loads(
        s3.get(
            "dev.processed.slack/2021-03-18/json-processed/messages/C01FHG8T7J5__slack-ingest/2021-03-18__0-0.json"
        )
    )
    pprint(normal_channel)
    ID = ("ips-C01FHG8T7J5-210318-0",)
    assert normal_channel[0]["_source"]["body"] == "And messages in a normal channel"

    """
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


def test_date_not_found_exception():
    MISSING_DATE = "2000-01-01"
    print("error")
    with pytest.raises(sed.NoDataFoundException) as e:
        sed.download(CLIENT_NAME, MISSING_DATE)
    assert "Could not find requested date" in str(e.value)
