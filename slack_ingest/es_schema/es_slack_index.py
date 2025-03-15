"""

This document defines the schema/mapping for Elasticsearch for the SlackDocument type.
It includes a run section like in es_index_management.py for creating the index in ES with
this mapping.


Schema 1 - Initial schema

"""
from datetime import datetime

import certifi
import settings
from elasticsearch_dsl import (
    Boolean,
    CustomField,
    Date,
    Document,
    InnerDoc,
    Integer,
    Keyword,
    Nested,
    Object,
    Search,
    Text,
    analyzer,
    connections,
)

# from src.teams_data_download.elastic_search.es_index_management import manageESIndex
from es_schema.es_index_management import manageESIndex

email_addr = analyzer(
    "email_addr",
    tokenizer="uax_url_email",
    filter=["lowercase", "stop"],
)

VERSION_NUMBER = 1
TEMPLATE_NAME = "slack-parse-v" + str(VERSION_NUMBER)
PATTERN = TEMPLATE_NAME + "-*"


class DataInput:
    alias = settings.ES_INPUT_INDEX  # "ips_data_input_slack"


class Schema:
    """Increment this number for each change rolled into production"""

    version = VERSION_NUMBER


class FingerprintDate(CustomField):
    builtin_type = "date"

    def _serialize(self, data: datetime):
        if data:
            return data.strftime("%Y-%m-%d %H:%M:%S")
        return None


class SlackId(InnerDoc):
    companyname = Keyword()
    emailaddress = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    uuid = Keyword()
    domain = Text(fields={"keyword": Keyword()})
    firstname = Text(fields={"keyword": Keyword()})
    lastname = Text(fields={"keyword": Keyword()})
    fullname = Text(fields={"keyword": Keyword()})
    slackid = Keyword()


class FingerprintMeta(InnerDoc):
    bucket = Keyword()
    client = Keyword()
    key = Keyword()
    processed_time = FingerprintDate(format="yyyy-MM-dd HH:mm:ss||E, dd MMM yyyy HH:mm:ss Z")
    time = FingerprintDate(format="yyyy-MM-dd HH:mm:ss||E, dd MMM yyyy HH:mm:ss Z")
    json_key = Keyword()
    type = Keyword()
    aws_lambda_id = Keyword()
    schema = Integer()
    """
      "fingerprint" : {
            "bucket" : "ayoracap.ips",
            "schema" : 6,
            "client" : "ayoracap",
            "time" : "2021-01-19 21:21:46",
            "type" : "bbg.im",
            "key" : "processed.bbg/2021-01-20/decoded/f889638.ib.210120.xml"
          },"""


class Sentiment(InnerDoc):
    compound = Integer()
    neg = Integer()
    neu = Integer()
    pos = Integer()


class BodyDetail(InnerDoc):
    body_sentiment = Object(Sentiment)
    body_size = Integer()
    has_body = Boolean()


class ItemId(InnerDoc):
    es_id = Text(fields={"keyword": Keyword()})
    item_date = Text(fields={"keyword": Keyword()})
    item_id = Text(fields={"keyword": Keyword()})
    item_number = Integer()


"""
"item_id" : {
            "item_date" : "210119",
            "item_id" : "0x2000001D86C55",
            "item_number" : "1284",
            "es_id" : "0x2000001D86C552101191284"
          },
"""


class Attachment(InnerDoc):
    filename = Keyword()
    content = Text(analyzer="english", term_vector="with_positions_offsets")
    filesize = Integer()
    error = Text()
    tar_file_location = Text()
    fileid = Keyword()


# TODO DELETE
# class AttachmentsDetail(InnerDoc):
#     has_attachment = Boolean()


class SlackDocument(Document):
    datetime = FingerprintDate(format="yyyy-MM-dd HH:mm:ss")
    attachments = Object(Attachment)
    # attachments_detail = Object(AttachmentsDetail) TODO DELETE
    conversationid = Keyword()
    fingerprint = Object(FingerprintMeta)
    from_ = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    from_detail = Object(SlackId)
    datetimeutc = FingerprintDate(format="yyyy-MM-dd HH:mm:ss")
    to = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    to_detail = Object(SlackId)
    body = Text(analyzer="english", term_vector="with_positions_offsets")
    body_detail = Object(BodyDetail)
    item_id = Object(ItemId)
    ts = Text(fields={"keyword": Keyword()})
    thread_ts = Text(fields={"keyword": Keyword()})

    class Index:
        settings = {"number_of_shards": 1, "number_of_replicas": 1}
        aliases: dict = {"ips_data_slack": {}}


if __name__ == "__main__":
    # Run the below code to create the initial mapping in Elasticsearch using the defined SlackDocument.

    import boto3

    # initiate the default connection to elasticsearch
    """stage = 'dev'
    ES_HOST = dict()
    ES_PASSWORD = dict()
    ES_HOST['dev'] = '98a8d377ae5e443b93c663ea55575976.eu-west-1.aws.found.io'
    ES_PASSWORD['dev'] = 'WFZjLsJmQ52qzcfkuDxQbgpk'
    """

    stage = "dev"
    ES_HOST = dict()
    ES_USER = dict()
    ES_PASSWORD = dict()

    ssm = boto3.client("ssm")

    # Get direct from AWS Parameter Store.
    ES_HOST[stage] = ssm.get_parameter(Name=f"/elastic_cluster/{stage}")["Parameter"]["Value"]
    ES_USER[stage] = ssm.get_parameter(Name=f"/elastic_app/{stage}/slack/user")["Parameter"]["Value"]
    ES_PASSWORD[stage] = ssm.get_parameter(Name=f"/elastic_app/{stage}/slack/password", WithDecryption=True)["Parameter"]["Value"]

    es_host = ES_HOST[stage]
    es_user = ES_USER[stage]
    es_password = ES_PASSWORD[stage]

    connections.create_connection(
        alias="default",
        hosts=[es_host],
        http_auth=(es_user, es_password),
        scheme="https",
        timeout=60,
        port=9243,
    )

    # create the empty index

    es_index_manage = manageESIndex()
    es_index_manage.dslDocument = SlackDocument
    es_index_manage.templateName = TEMPLATE_NAME
    es_index_manage.indexPattern = PATTERN
    es_index_manage.dataInputAlias = DataInput.alias
    es_index_manage.template()
