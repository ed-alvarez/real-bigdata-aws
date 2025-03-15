from fnmatch import fnmatch

from elasticsearch_dsl import (
    Boolean,
    CustomField,
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

from whatsapp_ingest.whatsapp_helpers.es_index_management import manageESIndex

VERSION_NUMBER = 1
TEMPLATE_NAME = "ips-data-whatsapp-v" + str(VERSION_NUMBER)
PATTERN = TEMPLATE_NAME + "-*"

html_strip = analyzer("html_strip", tokenizer="uax_url_email", char_filter=["html_strip"])

email_addr = analyzer("email_addr", tokenizer="uax_url_email")


class Schema:
    """Increment this number for each change rolled into production"""

    version = VERSION_NUMBER


class DataInput:
    alias = "ips_data_input_whatsapp"


class fingerprintDate(CustomField):
    builtin_type = "date"

    def _serialize(self, data):
        if data:
            return data.strftime("%Y-%m-%d %H:%M:%S")
        return None


class Whatsapp_Id(InnerDoc):
    corporateemailaddress = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    whatsapp_id = Keyword()
    domain = Text(fields={"keyword": Keyword()})


class Fingerprint_Meta(InnerDoc):
    bucket = Keyword()
    client = Keyword()
    key = Keyword()
    processed_time = fingerprintDate(format="yyyy-MM-dd HH:mm:ss")
    time = fingerprintDate(format="yyyy-MM-dd HH:mm:ss")
    type = Keyword()
    aws_lambda_id = Keyword()
    ses_message_id = Keyword()
    schema = Integer()


class Attachment(InnerDoc):
    filename = Keyword()
    content = Text(analyzer="english", term_vector="with_positions_offsets")
    type = Keyword()
    sub_type = Keyword()
    attachment_size = Integer()
    error = Text()


class AttachmentDetail(InnerDoc):
    has_attachment = Boolean()


class Sentiment(InnerDoc):
    compound = Integer()
    neg = Integer()
    neu = Integer()
    pos = Integer()


class BodyDetail(InnerDoc):
    body_sentiment = Object(Sentiment)
    body_size = Integer()
    has_body = Boolean()


class SubjectDetail(InnerDoc):
    subject_sentiment = Object(Sentiment)
    has_subject = Boolean()


class MessageIDDetail(InnerDoc):
    has_thread = Boolean()
    thread_index = Keyword()
    group_name = Text(fields={"keyword": Keyword()})
    group_id = Keyword()
    message_id = Keyword()


class WHATSAPP(Document):
    to = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    to_detail = Object(Whatsapp_Id)
    from_ = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    from_detail = Object(Whatsapp_Id)
    message_id_details = Object(MessageIDDetail)
    date = Date(format="E, d MMM yyyy HH:mm:ss Z||E, dd MMM yyyy HH:mm:ss Z||yyyy-MM-dd HH:mm:ss||yyyy-MM-dd'T'HH:mm:ss")

    body = Text(term_vector="with_positions_offsets")
    body_detail = Object(BodyDetail)
    subject = Text()
    subject_detail = Object(SubjectDetail)
    fingerprint = Object(Fingerprint_Meta)
    attachments = Object(Attachment)
    attachments_detail = Object(AttachmentDetail)

    @classmethod
    def _matches(cls, hit):
        # override _matches to match indices in a pattern instead of just ALIAS
        # hit is the raw dict as returned by elasticsearch
        return fnmatch(hit["_index"], PATTERN)

    class Index:
        name = "ips_data_input_whatsapp"
        settings = {"number_of_shards": 1, "number_of_replicas": 1}
        aliases = {"ips_data_whatsapp": {}}


if __name__ == "__main__":
    import boto3

    stage = "dev"
    ssm = boto3.client("ssm")
    es_host = ssm.get_parameter(Name=f"/elastic_cluster/dev")["Parameter"]["Value"]
    es_password = ssm.get_parameter(Name=f"/elastic_app/dev/elastic", WithDecryption=True)["Parameter"]["Value"]

    connections.create_connection(hosts=[es_host], http_auth=("elastic", es_password), scheme="https", timeout=60, port=9243)

    es_index_manage = manageESIndex()
    es_index_manage.dslDocument = WHATSAPP
    es_index_manage.templateName = TEMPLATE_NAME
    es_index_manage.indexPattern = PATTERN
    es_index_manage.dataInputAlias = DataInput.alias
    es_index_manage.template()
