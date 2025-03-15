"""
Schema 3 -  Added aws_lambda_id = Keyword()
            Updated processed -> processed_tiem
Schema 4 -  Added domain to bloomberg_id
            modified Attachment with content object
Schema 5 - Updated for New Cluster

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

email_addr = analyzer(
    "email_addr",
    tokenizer="uax_url_email",
    filter=["lowercase", "stop"],
)

VERSION_NUMBER = 6
TEMPLATE_NAME = "bbg-parse-ib-v" + str(VERSION_NUMBER)
PATTERN = TEMPLATE_NAME + "-*"


class DataInput:
    alias = "ips_data_input_bbg_ib"


class Schema:
    """Increment this number for each change rolled into production"""

    version = VERSION_NUMBER


class bloomberg_id(InnerDoc):
    accountnumber = Keyword()
    companyname = Keyword()
    emailaddress = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    uuid = Keyword()
    corporateemailaddress = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    domain = Text(fields={"keyword": Keyword()})
    firmnumber = Keyword()
    firstname = Text(fields={"keyword": Keyword()})
    lastname = Text(fields={"keyword": Keyword()})
    loginname = Keyword()


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


class item_id(InnerDoc):
    es_id = Text(fields={"keyword": Keyword()})
    item_date = Text(fields={"keyword": Keyword()})
    item_id = Text(fields={"keyword": Keyword()})
    item_number = Integer()


class attachment(InnerDoc):
    filename = Keyword()
    content = Text(analyzer="english", term_vector="with_positions_offsets")
    filesize = Integer()
    error = Text()
    fileB64content = Text(term_vector="with_positions_offsets")
    tar_file_location = Text()
    fileid = Keyword()


class BBG_IB(Document):
    datetime = Date(format="MM/dd/yyyy HH:mm:ss")
    attachments = Object(attachment)
    conversationid = Keyword()
    fingerprint = Object(fingerprint_meta)
    from_detail = Object(bloomberg_id)
    from_ = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    datetimeutc = Date()
    to_detail = Object(bloomberg_id)
    to = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    body = Text(analyzer="english", term_vector="with_positions_offsets")
    item_id = Object(item_id)

    class Index:
        settings: dict = {"number_of_shards": 1, "number_of_replicas": 1}
        aliases: dict = {"ips_data_bbg_ib": {}}


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
    es_index_manage.dslDocument = BBG_IB
    es_index_manage.templateName = TEMPLATE_NAME
    es_index_manage.indexPattern = PATTERN
    es_index_manage.dataInputAlias = DataInput.alias
    es_index_manage.template()
