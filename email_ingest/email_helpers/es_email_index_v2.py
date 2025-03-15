from elasticsearch_dsl import (
    Boolean,
    CustomField,
    Document,
    InnerDoc,
    Integer,
    Keyword,
    Object,
    Text,
    analyzer,
    connections,
)
from email_helpers.es_index_management import manageESIndex

VERSION_NUMBER = 2
TEMPLATE_NAME = "ips-data-email-v" + str(VERSION_NUMBER)
PATTERN = TEMPLATE_NAME + "-*"


class Schema:
    """Increment this number for each change rolled into production"""

    version = VERSION_NUMBER


class DataInput:
    alias = "ips_data_input_email"


html_strip = analyzer("html_strip", tokenizer="uax_url_email", char_filter=["html_strip"])

email_addr = analyzer(
    "email_addr",
    tokenizer="uax_url_email",
    filter=["lowercase", "stop"],
)


class fingerprintDate(CustomField):
    builtin_type = "date"

    def _serialize(self, data):
        if data:
            return data.strftime("%Y-%m-%d %H:%M:%S")
        return None


class Email_Id(InnerDoc):
    corporateemailaddress = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    firstname = Text(fields={"keyword": Keyword()})
    lastname = Text(fields={"keyword": Keyword()})
    domain = Text(fields={"keyword": Keyword()})


class Fingerprint_Meta(InnerDoc):
    bucket = Keyword()
    client = Keyword()
    key = Keyword()
    processed_time = fingerprintDate(format="yyyy-MM-dd HH:mm:ss||E, dd MMM yyyy HH:mm:ss Z")
    time = fingerprintDate(format="yyyy-MM-dd HH:mm:ss||E, dd MMM yyyy HH:mm:ss Z")
    type = Keyword()
    aws_lambda_id = Keyword()
    ses_message_id = Keyword()
    schema = Integer()


class Attachment(InnerDoc):
    filename = Keyword()
    content = Text(analyzer="english", term_vector="with_positions_offsets")
    attachment_size = Integer()
    error = Text()


class AttachmentsDetail(InnerDoc):
    has_attachment = Boolean()


class Sentiment(InnerDoc):
    compound = Integer()
    neg = Integer()
    neu = Integer()
    pos = Integer()


class SubjectDetail(InnerDoc):
    subject_sentiment = Object(Sentiment)
    has_subject = Boolean()


class BodyDetail(InnerDoc):
    body_sentiment = Object(Sentiment)
    full_body = Text(analyzer="english", term_vector="with_positions_offsets")
    body_size = Integer()
    has_body = Boolean()


class MessageIDDetail(InnerDoc):
    has_thread = Boolean()
    thread_index = Keyword()
    thread_topic = Keyword()


class EMAIL(Document):
    to = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    to_detail = Object(Email_Id)
    from_ = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    from_detail = Object(Email_Id)
    cc = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    cc_detail = Object(Email_Id)
    bcc = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    bcc_detail = Object(Email_Id)
    subject = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    subject_detail = Object(SubjectDetail)
    body = Text(analyzer="english", term_vector="with_positions_offsets")
    body_detail = Object(BodyDetail)
    attachments = Object(Attachment)
    attachments_detail = Object(AttachmentsDetail)
    message_id = Keyword()
    message_id_detail = Object(MessageIDDetail)
    date = fingerprintDate(format="yyyy-MM-dd HH:mm:ss")
    fingerprint = Object(Fingerprint_Meta)

    class Index:
        name = "ips_data_input_email"
        settings = {"number_of_shards": 1, "number_of_replicas": 1}
        aliases = {"ips_data_email": {}}


if __name__ == "__main__":
    # initiate the default connection to elasticsearch

    stage = "dev"
    ES_HOST = dict()
    ES_PASSWORD = dict()
    ES_HOST["dev"] = "98a8d377ae5e443b93c663ea55575976.eu-west-1.aws.found.io"
    ES_PASSWORD["dev"] = "WFZjLsJmQ52qzcfkuDxQbgpk"

    es_host = ES_HOST[stage]
    es_password = ES_PASSWORD[stage]

    connections.create_connection(hosts=[es_host], http_auth=("elastic", es_password), scheme="https", timeout=60, port=9243)

    es_index_manage = manageESIndex()
    es_index_manage.dslDocument = EMAIL
    es_index_manage.templateName = TEMPLATE_NAME
    es_index_manage.indexPattern = PATTERN
    es_index_manage.dataInputAlias = DataInput.alias
    es_index_manage.template()
