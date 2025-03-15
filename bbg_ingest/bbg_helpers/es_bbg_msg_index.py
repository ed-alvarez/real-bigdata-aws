"""
Schema 3 -  Fingerprint
            Added aws_lambda_id = Keyword()
            Updated processed -> processed_time
            Attachments
            added tar_file_location = Text()
            Bloomberg_ID
            added domain = Keyword()
Schema 4 -  Update for New Cluster

"""

from bbg_helpers.es_index_management import manageESIndex
from elasticsearch_dsl import (
    Date,
    Document,
    InnerDoc,
    Integer,
    Keyword,
    Object,
    Text,
    analyzer,
    connections,
)

"""Increment this number for each change rolled into production"""
VERSION_NUMBER = 5
TEMPLATE_NAME = "bbg-parse-msg-v" + str(VERSION_NUMBER)
PATTERN = TEMPLATE_NAME + "-*"

email_addr = analyzer(
    "email_addr",
    tokenizer="uax_url_email",
    filter=["lowercase", "stop"],
)


class Schema:
    version = VERSION_NUMBER


class DataInput:
    alias = "ips_data_input_bbg_msg"


class bloomberg_id(InnerDoc):
    accountname = Text(fields={"keyword": Keyword()})
    accountnumber = Keyword()
    bloombergemailaddress = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    bloomberguuid = Keyword()
    corporateemailaddress = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    domain = Text(fields={"keyword": Keyword()})
    firmnumber = Keyword()
    firstname = Text(fields={"keyword": Keyword()})
    lastname = Text(fields={"keyword": Keyword()})
    loginname = Keyword()
    companyname = Keyword()


class fingerprint_meta(InnerDoc):
    bucket = Keyword()
    processed_time = Date(format="E, dd MMM yyyy HH:mm:ss Z||yyyy-MM-dd HH:mm:ss")
    json_key = Keyword()
    client = Keyword()
    time = Date(format="E, dd MMM yyyy HH:mm:ss Z||yyyy-MM-dd HH:mm:ss")
    type = Keyword()
    key = Keyword()
    aws_lambda_id = Keyword()
    schema = Integer()


class attachment(InnerDoc):
    filename = Keyword()
    content = Text(analyzer="english", term_vector="with_positions_offsets")
    filesize = Integer()
    error = Text()
    tar_file_location = Text()
    fileid = Keyword()


class BBG_MSG(Document):
    attachments = Object(attachment)
    bcc = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    bcc_detail = Object(bloomberg_id)
    body = Text(analyzer="english", term_vector="with_positions_offsets")
    cc = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    cc_detail = Object(bloomberg_id)
    date = Date(format="yyyy-MM-dd HH:mm:ss||yyyy-MM-dd'T'HH:mm:ss")
    disclaimerreference = Keyword()
    fingerprint = Object(fingerprint_meta)
    from_ = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    from_detail = Object(bloomberg_id)
    from_orig = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    from_orig_detail = Object(bloomberg_id)
    greeting = Text()
    msgid = Keyword()
    msglang = Keyword()
    msgtimeutc = Date()
    msgtype = Keyword()
    subject = Text()
    to = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    to_detail = Object(bloomberg_id)

    class Index:
        settings = {"number_of_shards": 1, "number_of_replicas": 1}
        aliases = {"ips_data_bbg_msg": {}}


if __name__ == "__main__":
    # initiate the default connection to elasticsearch
    stage = "dev"
    ES_HOST = dict()
    ES_PASSWORD = dict()
    ES_HOST["dev"] = "98a8d377ae5e443b93c663ea55575976.eu-west-1.aws.found.io"
    ES_PASSWORD["dev"] = "WFZjLsJmQ52qzcfkuDxQbgpk"

    es_host = ES_HOST[stage]
    es_password = ES_PASSWORD[stage]

    connections.create_connection(
        alias="default",
        hosts=[es_host],
        http_auth=("elastic", es_password),
        scheme="https",
        timeout=60,
        port=9243,
    )

    # create the empty index

    es_index_manage = manageESIndex()
    es_index_manage.dslDocument = BBG_MSG
    es_index_manage.templateName = TEMPLATE_NAME
    es_index_manage.indexPattern = PATTERN
    es_index_manage.dataInputAlias = DataInput.alias
    es_index_manage.template()
