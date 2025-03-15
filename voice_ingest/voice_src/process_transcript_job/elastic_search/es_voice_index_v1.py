from elasticsearch_dsl import (
    Boolean,
    CustomField,
    Document,
    Float,
    InnerDoc,
    Integer,
    Keyword,
    Object,
    Text,
    connections,
)
from voice_src.process_transcript_job.elastic_search.es_index_management import (
    manageESIndex,
)

VERSION_NUMBER = 1
TEMPLATE_NAME = "ips-data-voice-v" + str(VERSION_NUMBER)
PATTERN = TEMPLATE_NAME + "-*"


class Schema:
    """Increment this number for each change rolled into production"""

    version = VERSION_NUMBER


class DataInput:
    alias = "ips_data_input_voice"


class fingerprintDate(CustomField):
    builtin_type = "date"

    def _serialize(self, data):
        if data:
            return data.strftime("%Y-%m-%d %H:%M:%S")
        return None


class Call_Id(InnerDoc):
    corporateemailaddress = Text(fields={"keyword": Keyword()})
    firstname = Text(fields={"keyword": Keyword()})
    lastname = Text(fields={"keyword": Keyword()})
    domain = Text(fields={"keyword": Keyword()})
    tel_number = Text(fields={"keyword": Keyword()})


class Fingerprint_Meta(InnerDoc):
    bucket = Keyword()
    client = Keyword()
    key_audio = Keyword()
    key_cdr = Keyword()
    key_transcript = Keyword()
    processed_time = fingerprintDate(format="yyyy-MM-dd HH:mm:ss")
    time = fingerprintDate(format="yyyy-MM-dd HH:mm:ss")
    type = Keyword()
    type_source = Keyword()
    type_transcription = Keyword()
    aws_lambda_id = Keyword()
    schema = Integer()


class Sentiment(InnerDoc):
    summary = Keyword()
    compound = Integer()
    neg = Float()
    neu = Float()
    pos = Float()


class Phrase(InnerDoc):
    start_time = Float()
    end_time = Float()
    text = Text(analyzer="english", term_vector="with_positions_offsets")
    entities = Keyword()
    key_phrases = Keyword()
    speaker = Keyword()
    gap = Float()
    sentiment = Object(Sentiment)
    reason = Text()


class BodyDetail(InnerDoc):
    phrases = Object(Phrase)
    has_body = Boolean()


class VOICE(Document):
    to = Text(fields={"keyword": Keyword()})
    to_detail = Object(Call_Id)
    from_ = Text(fields={"keyword": Keyword()})
    from_detail = Object(Call_Id)
    body = Text(analyzer="english", term_vector="with_positions_offsets")
    body_detail = Object(BodyDetail)
    date = fingerprintDate(format="yyyy-MM-dd HH:mm:ss")
    fingerprint = Object(Fingerprint_Meta)

    class Index:
        settings = {"number_of_shards": 1, "number_of_replicas": 1}
        aliases = {"ips_data_voice": {}}


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
    es_index_manage.dslDocument = VOICE
    es_index_manage.templateName = TEMPLATE_NAME
    es_index_manage.indexPattern = PATTERN
    es_index_manage.dataInputAlias = DataInput.alias
    es_index_manage.template()
