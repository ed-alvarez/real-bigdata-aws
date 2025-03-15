import json
from datetime import datetime

import es_schema as ess
import helpers.es
import helpers.es_bulk_uploader
import helpers.es_slack_id
import helpers.fingerprint_db
import helpers.s3
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

CLIENT_NAME = "ips"
DATE_Y_M_D = "2021-02-01"

users_json = """[ {
  "id": "U01EX0CCK0E",
  "team_id": "TP2JMH5U3",
  "name": "anthony",
  "deleted": false,
  "color": "e0a729",
  "real_name": "anthony",
  "tz": "Europe/London",
  "tz_label": "Greenwich Mean Time",
  "tz_offset": 0,
  "profile": {
   "title": "",
   "phone": "",
   "skype": "",
   "real_name": "anthony",
   "real_name_normalized": "anthony",
   "display_name": "",
   "display_name_normalized": "",
   "fields": null,
   "status_text": "",
   "status_emoji": "",
   "status_expiration": 0,
   "avatar_hash": "g8b6be86dd5c",
   "image_24": "https://secure.gravatar.com/avatar/8b6be86dd5c80c892c907a9410b5ab1b.jpg?s=24&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0009-24.png",
   "image_32": "https://secure.gravatar.com/avatar/8b6be86dd5c80c892c907a9410b5ab1b.jpg?s=32&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0009-32.png",
   "image_48": "https://secure.gravatar.com/avatar/8b6be86dd5c80c892c907a9410b5ab1b.jpg?s=48&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0009-48.png",
   "image_72": "https://secure.gravatar.com/avatar/8b6be86dd5c80c892c907a9410b5ab1b.jpg?s=72&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0009-72.png",
   "image_192": "https://secure.gravatar.com/avatar/8b6be86dd5c80c892c907a9410b5ab1b.jpg?s=192&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0009-192.png",
   "image_512": "https://secure.gravatar.com/avatar/8b6be86dd5c80c892c907a9410b5ab1b.jpg?s=512&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0009-512.png",
   "status_text_canonical": "",
   "team": "TP2JMH5U3"
  },
  "is_admin": true,
  "is_owner": true,
  "is_primary_owner": false,
  "is_restricted": false,
  "is_ultra_restricted": false,
  "is_bot": false,
  "is_app_user": false,
  "updated": 1605877526,
  "is_email_confirmed": true,
  "has_2fa": false
 },
 {
  "id": "UP2JNQM9R",
  "team_id": "TP2JMH5U3",
  "name": "tom",
  "deleted": false,
  "color": "3c989f",
  "real_name": "Tom Vavrechka",
  "tz": "Europe/London",
  "tz_label": "Greenwich Mean Time",
  "tz_offset": 0,
  "profile": {
   "title": "",
   "phone": "+447443323375",
   "skype": "",
   "real_name": "Tom Vavrechka",
   "real_name_normalized": "Tom Vavrechka",
   "display_name": "Tom",
   "display_name_normalized": "Tom",
   "fields": null,
   "status_text": "",
   "status_emoji": "",
   "status_expiration": 0,
   "avatar_hash": "gc4495e38582",
   "first_name": "Tom",
   "last_name": "Vavrechka",
   "image_24": "https://secure.gravatar.com/avatar/c4495e38582e03ae164ae4725fadff73.jpg?s=24&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0007-24.png",
   "image_32": "https://secure.gravatar.com/avatar/c4495e38582e03ae164ae4725fadff73.jpg?s=32&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0007-32.png",
   "image_48": "https://secure.gravatar.com/avatar/c4495e38582e03ae164ae4725fadff73.jpg?s=48&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0007-48.png",
   "image_72": "https://secure.gravatar.com/avatar/c4495e38582e03ae164ae4725fadff73.jpg?s=72&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0007-72.png",
   "image_192": "https://secure.gravatar.com/avatar/c4495e38582e03ae164ae4725fadff73.jpg?s=192&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0007-192.png",
   "image_512": "https://secure.gravatar.com/avatar/c4495e38582e03ae164ae4725fadff73.jpg?s=512&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0007-512.png",
   "status_text_canonical": "",
   "team": "TP2JMH5U3"
  },
  "is_admin": false,
  "is_owner": false,
  "is_primary_owner": false,
  "is_restricted": false,
  "is_ultra_restricted": false,
  "is_bot": false,
  "is_app_user": false,
  "updated": 1571155915,
  "is_email_confirmed": true,
  "has_2fa": false
 },
{
  "id": "UPFUKHWS3",
  "team_id": "TP2JMH5U3",
  "name": "sean",
  "deleted": false,
  "color": "4bbe2e",
  "real_name": "Sean Morgan",
  "tz": "Europe/London",
  "tz_label": "Greenwich Mean Time",
  "tz_offset": 0,
  "profile": {
   "title": "eComms Surveillance for Financial Crime & Suspicious Activity",
   "phone": "+447444879549",
   "skype": "",
   "real_name": "Sean Morgan",
   "real_name_normalized": "Sean Morgan",
   "display_name": "Sean Morgan",
   "display_name_normalized": "Sean Morgan",
   "fields": null,
   "status_text": "",
   "status_emoji": "",
   "status_expiration": 0,
   "avatar_hash": "1c71adf9e86e",
   "image_original": "https://avatars.slack-edge.com/2019-10-16/797192641621_1c71adf9e86e4d1832f3_original.jpg",
   "is_custom_image": true,
   "first_name": "Sean",
   "last_name": "Morgan",
   "image_24": "https://avatars.slack-edge.com/2019-10-16/797192641621_1c71adf9e86e4d1832f3_24.jpg",
   "image_32": "https://avatars.slack-edge.com/2019-10-16/797192641621_1c71adf9e86e4d1832f3_32.jpg",
   "image_48": "https://avatars.slack-edge.com/2019-10-16/797192641621_1c71adf9e86e4d1832f3_48.jpg",
   "image_72": "https://avatars.slack-edge.com/2019-10-16/797192641621_1c71adf9e86e4d1832f3_72.jpg",
   "image_192": "https://avatars.slack-edge.com/2019-10-16/797192641621_1c71adf9e86e4d1832f3_192.jpg",
   "image_512": "https://avatars.slack-edge.com/2019-10-16/797192641621_1c71adf9e86e4d1832f3_512.jpg",
   "image_1024": "https://avatars.slack-edge.com/2019-10-16/797192641621_1c71adf9e86e4d1832f3_1024.jpg",
   "status_text_canonical": "",
   "team": "TP2JMH5U3"
  },
  "is_admin": false,
  "is_owner": false,
  "is_primary_owner": false,
  "is_restricted": false,
  "is_ultra_restricted": false,
  "is_bot": false,
  "is_app_user": false,
  "updated": 1571439805,
  "is_email_confirmed": true,
  "has_2fa": false
 }
 ]
"""


def get_users_from_slack_string():
    users = json.loads(users_json)
    return {user["id"]: user for user in users}


def test_create_slack_es_document():
    DATETIME = datetime.now()
    DATETIMEUTC = datetime.utcnow()
    MESSAGE_TEXT = "text message 123"
    TS = "1612521204.001000"
    s3 = helpers.s3.S3(CLIENT_NAME, DATE_Y_M_D)
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(MESSAGE_TEXT)
    message = {
        "from": "UP2JNQM9R",  # Tom Vavrechka
        "to": ["to user", "U01EX0CCK0E", "UPFUKHWS3"],  # anthony, sean
        "text": MESSAGE_TEXT,
        "datetime": DATETIME,
        "datetimeutc": DATETIMEUTC,
        "sentiment": sentiment,
        "ts": TS,
    }
    channel_message_number = 168
    channel_id = "C000001"
    channel_label = "C000001__testchannel"
    channels = {}
    users = {}
    slack_users_dict = get_users_from_slack_string()
    fingerprintdb_users_dict = helpers.fingerprint_db.get_fingerprint_users_for_client(CLIENT_NAME)
    es_slack_id_inner_doc_creator = helpers.es_slack_id.SlackIdInnerDocCreator(CLIENT_NAME, fingerprintdb_users_dict, slack_users_dict)

    sd = helpers.es.create_es_slack_document(
        message,
        CLIENT_NAME,
        s3,
        channel_message_number,
        channel_id,
        channel_label,
        channels,
        users,
        es_slack_id_inner_doc_creator,
    )
    assert sd.body == MESSAGE_TEXT
    assert sd.item_id.item_number == 168
    """ Fingerprint Meta
    bucket = f'{client_name}.ips',
    client = client_name,
    time = dt,
    type = 'slack'
    processed_time = datetime.now(),
    schema = ess.VERSION,
    key = processed_key)
    """
    fp = sd.fingerprint
    assert fp.bucket == f"{CLIENT_NAME}.ips"
    assert fp.client == CLIENT_NAME
    # assert(fpm.time.strftime("%Y%m%d %H:%M:%S") == datetime.now().strftime("%Y%m%d %H:%M:%S"))
    assert fp.time == DATETIME
    # assert(fp.type == 'slack.channel')
    assert fp.type == "slack"
    assert fp.processed_time.strftime("%Y%m%d") == datetime.now().strftime(
        "%Y%m%d"
    )  # Compare date as minutes as seconds can change in test
    # assert(fpm.processed_time == DATETIME)
    assert fp.schema == ess.es_slack_index.VERSION_NUMBER
    assert fp.key.startswith("processed.slack") or fp.key.startswith("dev.processed.slack")
    print(sd.item_id)
    ii = sd.item_id
    print(ii.es_id)
    assert ii.item_id == f"{CLIENT_NAME}-{channel_id}"
    assert ii.item_number == channel_message_number
    yymmdd = DATETIME.strftime("%y%m%d")
    assert ii.item_date == yymmdd
    assert ii.es_id == f"{CLIENT_NAME}-{channel_id}-{yymmdd}-{channel_message_number}"
    print(sentiment)
    print(type(sentiment))
    assert sd.body_detail.body_sentiment.neu == 1.0
    print(type(sd.attachments))
    print(sd.attachments.filename)
    assert sd.attachments.filename is None
    assert sd.thread_ts is None
    print(sd.to[0] + "1")
    print(sd.to[1] + "1")
    assert sd.to[0] == "Sean Morgan <None>"
    assert sd.to[1] == "anthony <None>" and sd.to[2] == "to user <None>"
    assert sd.to_detail[0].fullname == "Sean Morgan"
    assert sd.from_ == "Tom Vavrechka <None>"
    assert sd.from_detail.fullname == "Tom Vavrechka"


def test_create_attachment_document():
    DATETIME = datetime.now()
    DATETIMEUTC = datetime.utcnow()
    MESSAGE_TEXT = "text message 345"
    TS = "1612521204.001000"
    s3 = helpers.s3.S3(CLIENT_NAME, DATE_Y_M_D)
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(MESSAGE_TEXT)
    message = {
        "from": "U01EX0CCK0E",
        "to": ["to user att", "UPG9G6D38"],
        "text": MESSAGE_TEXT,
        "datetime": DATETIME,
        "datetimeutc": DATETIMEUTC,
        "sentiment": sentiment,
        "ts": TS,
    }
    channel_message_number = 168
    channel_id = "D000002"
    channel_label = f"{channel_id}__testdirectconv"
    channels = {}
    users = {}
    FILE_SLACK_ID = "F01LEAP7R9B"
    FILENAME = "a file name.docx"
    FILE_SIZE = "248"
    ATTACHMENT_TEXT = "some text for the attachment"
    ERROR = ""
    PROCESSED_S3_PATH = f"dev.processed.slack/2021-02-01/attachments/{FILE_SLACK_ID}.tgz"

    slack_users_dict = get_users_from_slack_string()
    fingerprintdb_users_dict = helpers.fingerprint_db.get_fingerprint_users_for_client(CLIENT_NAME)
    es_slack_id_inner_doc_creator = helpers.es_slack_id.SlackIdInnerDocCreator(CLIENT_NAME, fingerprintdb_users_dict, slack_users_dict)

    asd = helpers.es.create_es_attachment_slack_document(
        FILE_SLACK_ID,
        FILENAME,
        FILE_SIZE,
        ATTACHMENT_TEXT,
        ERROR,
        PROCESSED_S3_PATH,
        message,
        CLIENT_NAME,
        s3,
        channel_message_number,
        channel_id,
        channel_label,
        channels,
        users,
        es_slack_id_inner_doc_creator,
    )

    assert asd.body == ""
    # Main document checks (copied from above test case)
    # assert (asd.body == MESSAGE_TEXT)
    assert asd.item_id.item_number == 168
    """ Fingerprint Meta
    bucket = f'{client_name}.ips',
    client = client_name,
    time = dt,
    type = 'slack'
    processed_time = datetime.now(),
    schema = ess.VERSION,
    key = processed_key)
    """
    fp = asd.fingerprint
    assert fp.bucket == f"{CLIENT_NAME}.ips"
    assert fp.client == CLIENT_NAME
    # assert(fpm.time.strftime("%Y%m%d %H:%M:%S") == datetime.now().strftime("%Y%m%d %H:%M:%S"))
    assert fp.time == DATETIME
    # assert (fp.type == 'slack.direct')
    assert fp.type == "slack"
    assert fp.processed_time.strftime("%Y%m%d") == datetime.now().strftime(
        "%Y%m%d"
    )  # Removed seconds as fluke would sometimes make them one second apart.
    # assert(fpm.processed_time == DATETIME)
    assert fp.schema == ess.es_slack_index.VERSION_NUMBER
    assert fp.key.startswith("processed.slack") or fp.key.startswith("dev.processed.slack")
    print(asd.item_id)
    ii = asd.item_id
    print(ii.es_id)
    assert ii.item_id == f"{CLIENT_NAME}-{channel_id}"
    assert ii.item_number == channel_message_number
    yymmdd = DATETIME.strftime("%y%m%d")
    assert ii.item_date == yymmdd
    assert ii.es_id == f"{CLIENT_NAME}-{channel_id}-{yymmdd}-{channel_message_number}"

    # Attachment document checks
    # print(sentiment)
    # print(type(sentiment))
    print(asd.body_detail.body_sentiment.neu)
    assert asd.body_detail.body_sentiment.neu is None
    print(type(asd.attachments), type(asd.attachments[0]))
    assert len(asd.attachments) == 1
    print(asd.attachments[0].filename)
    assert asd.attachments[0].filename is FILENAME
    assert asd.attachments[0].filesize is FILE_SIZE
    assert asd.attachments[0].error is ERROR
    assert asd.attachments[0].tar_file_location is PROCESSED_S3_PATH
    assert asd.attachments[0].fileid is FILE_SLACK_ID
    assert asd.attachments[0].content is ATTACHMENT_TEXT
    assert asd.to[0] == "James TEST Hogbin <james@fingerprint-supervision.com>"
    assert asd.to[1] == "to user att <None>"
    assert asd.to_detail[0].firstname == "James"
    assert asd.to_detail[0].companyname == "IP Sentinel"
    assert asd.to_detail[1].firstname is None
    assert asd.from_ == "anthony <None>"


def test_create_slack_es_document_with_thread_ts():
    # Thread ts should be appended to item_id/conversationid after a double dot
    # i.e. C120343..13291302102910.091231
    DATETIME = datetime.now()
    DATETIMEUTC = datetime.utcnow()
    MESSAGE_TEXT = "text message 123"
    TS = "1612521213.001100"
    THREAD_TS = "1612521204.001000"
    s3 = helpers.s3.S3(CLIENT_NAME, DATE_Y_M_D)
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(MESSAGE_TEXT)
    THREAD_TS = "1612435334.001000"
    message = {
        "from": "from user",
        "to": ["to user", "U01EX0CCK0E"],
        "text": MESSAGE_TEXT,
        "datetime": DATETIME,
        "datetimeutc": DATETIMEUTC,
        "sentiment": sentiment,
        "thread_ts": THREAD_TS,
        "ts": TS,
    }
    channel_message_number = 168
    channel_id = "C000001"
    channel_label = "C000001__testchannel"
    channels = {}
    users = {}
    slack_users_dict = get_users_from_slack_string()
    fingerprintdb_users_dict = helpers.fingerprint_db.get_fingerprint_users_for_client(CLIENT_NAME)
    es_slack_id_inner_doc_creator = helpers.es_slack_id.SlackIdInnerDocCreator(CLIENT_NAME, fingerprintdb_users_dict, slack_users_dict)
    sd = helpers.es.create_es_slack_document(
        message,
        CLIENT_NAME,
        s3,
        channel_message_number,
        channel_id,
        channel_label,
        channels,
        users,
        es_slack_id_inner_doc_creator,
    )
    assert sd.thread_ts == THREAD_TS
    assert sd.ts == TS


def test_es_bulk_dicts_from_slack_documents():
    DATETIME = datetime.now()
    DATETIMEUTC = datetime.utcnow()
    MESSAGE_TEXT = "Threaded message text 456"
    MESSAGE_TEXT_2 = "Message two in testing sequence"
    TS = "1612521213.001100"
    THREAD_TS = "1612521204.001000"
    s3 = helpers.s3.S3(CLIENT_NAME, DATE_Y_M_D)
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(MESSAGE_TEXT)
    THREAD_TS = "1612435334.001000"
    message = {
        "from": "UPG9G6D38",
        "to": ["to user", "U01EX0CCK0E"],
        "text": MESSAGE_TEXT,
        "datetime": DATETIME,
        "datetimeutc": DATETIMEUTC,
        "sentiment": sentiment,
        "thread_ts": THREAD_TS,
        "ts": TS,
    }
    channel_message_number = 168
    channel_id = "C000001"
    channel_label = "C000001__testchannel"
    channels = {}
    users = {}
    slack_users_dict = get_users_from_slack_string()
    fingerprintdb_users_dict = helpers.fingerprint_db.get_fingerprint_users_for_client(CLIENT_NAME)
    es_slack_id_inner_doc_creator = helpers.es_slack_id.SlackIdInnerDocCreator(CLIENT_NAME, fingerprintdb_users_dict, slack_users_dict)
    sd1 = helpers.es.create_es_slack_document(
        message,
        CLIENT_NAME,
        s3,
        channel_message_number,
        channel_id,
        channel_label,
        channels,
        users,
        es_slack_id_inner_doc_creator,
    )
    message["text"] = MESSAGE_TEXT_2
    DATETIME_2 = datetime.now()
    message["datetime"] = DATETIME_2
    sd2 = helpers.es.create_es_slack_document(
        message,
        CLIENT_NAME,
        s3,
        channel_message_number + 1,
        channel_id,
        channel_label,
        channels,
        users,
        es_slack_id_inner_doc_creator,
    )

    sds = [sd1, sd2]
    INDEX = "slack-parse-index-1"
    bulk_dicts = helpers.es_bulk_uploader._get_bulk_format_dicts_from_es_docs(INDEX, sds)
    DATEFORMAT = "%Y-%m-%d %H:%M:%S"
    for bd in bulk_dicts:
        assert bd["_source"]["item_id"]["es_id"] == bd["_id"]
        assert "body_sentiment" in bd["_source"]["body_detail"]
        assert bd["_index"] == INDEX
    assert bulk_dicts[0]["_source"]["body"] == MESSAGE_TEXT
    assert bulk_dicts[1]["_source"]["body"] == MESSAGE_TEXT_2
    assert bulk_dicts[0]["_source"]["datetime"] == DATETIME.strftime(DATEFORMAT)
    assert bulk_dicts[1]["_source"]["datetime"] == DATETIME_2.strftime(DATEFORMAT)
    print(bulk_dicts[1]["_source"])
    print(bulk_dicts[1]["_source"]["to"])
    print(bulk_dicts[1]["_source"]["to_detail"])
    to_detail = bulk_dicts[1]["_source"]["to_detail"]
    if "firstname" in to_detail[0]:
        assert to_detail[0]["firstname"] == "anthony" and to_detail[1]["slackid"] == "to user"
    else:
        assert to_detail[0]["slackid"] == "to user" and to_detail[1]["firstname"] == "anthony"
    print(bulk_dicts[1]["_source"]["from_"])
    assert bulk_dicts[1]["_source"]["from_"] == "James TEST Hogbin <james@fingerprint-supervision.com>"
    print(bulk_dicts[1]["_source"]["from_detail"])
    assert bulk_dicts[1]["_source"]["from_detail"]["firstname"] == "James"
    assert bulk_dicts[1]["_source"]["from_detail"]["companyname"] == "IP Sentinel"
