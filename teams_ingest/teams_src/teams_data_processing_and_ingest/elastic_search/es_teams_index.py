"""
Schema 2 - Initial schema

"""


from datetime import datetime

import certifi
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

email_addr = analyzer(
    "email_addr",
    tokenizer="uax_url_email",
    filter=["lowercase", "stop"],
)

VERSION_NUMBER = 1
TEMPLATE_NAME = f"teams-parse-v{VERSION_NUMBER}"
PATTERN = f"{TEMPLATE_NAME}-*"


class DataInput:
    alias = "ips_data_input_teams"


class Schema:
    """Increment this number for each change rolled into production"""

    version = VERSION_NUMBER


class fingerprintDate(CustomField):
    builtin_type = "date"

    def _serialize(self, data: datetime):
        return data.strftime("%Y-%m-%d %H:%M:%S") if data else None


class teams_id(InnerDoc):
    companyname = Keyword()
    emailaddress = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    uuid = Keyword()
    domain = Text(fields={"keyword": Keyword()})
    firstname = Text(fields={"keyword": Keyword()})
    lastname = Text(fields={"keyword": Keyword()})
    fullname = Text(fields={"keyword": Keyword()})


class fingerprint_meta(InnerDoc):
    bucket = Keyword()
    client = Keyword()
    key = Keyword()
    processed_time = fingerprintDate(format="yyyy-MM-dd HH:mm:ss")
    time = fingerprintDate(format="yyyy-MM-dd HH:mm:ss")
    type = Keyword()
    aws_lambda_id = Keyword()
    schema = Integer()


class Sentiment(InnerDoc):
    compound = Integer()
    neg = Integer()
    neu = Integer()
    pos = Integer()


class BodyDetail(InnerDoc):
    body_sentiment = Object(Sentiment)
    body_size = Integer()
    image_file_archive = Text()
    has_body = Boolean()


class attachment(InnerDoc):
    filename = Keyword()
    content = Text(analyzer="english", term_vector="with_positions_offsets")
    filesize = Integer()
    error = Text()
    tar_file_location = Text()
    fileid = Keyword()


class AttachmentsDetail(InnerDoc):
    has_attachment = Boolean()


class TEAMS(Document):
    datetime = fingerprintDate(format="yyyy-MM-dd HH:mm:ss")
    attachments = Object(attachment)
    attachments_detail = Object(AttachmentsDetail)
    conversationid = Keyword()
    messageid = Keyword()
    fingerprint = Object(fingerprint_meta)
    from_ = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    from_detail = Object(teams_id)
    datetimeutc = Date()
    to = Text(analyzer=email_addr, fields={"keyword": Keyword()})
    to_detail = Object(teams_id)
    body = Text(analyzer="english", term_vector="with_positions_offsets")
    body_detail = Object(BodyDetail)

    class Index:
        settings = {"number_of_shards": 1, "number_of_replicas": 1}
        aliases = {"ips_data_teams": {}}


class manageESIndex:
    def __init__(self):
        self._template_name = str()
        self._index_pattern = str()
        self._dsl_document = Document()
        self._data_input_alias = str()
        self._move_data = False
        self._update_input_alias = True
        self._es = None

    @property
    def templateName(self):
        return self._template_name

    @templateName.setter
    def templateName(self, value):
        self._template_name = value

    @property
    def indexPattern(self):
        return self._index_pattern

    @indexPattern.setter
    def indexPattern(self, value):
        self._index_pattern = value

    @property
    def dslDocument(self):
        return self._dsl_document

    @dslDocument.setter
    def dslDocument(self, value):
        self._dsl_document = value

    @property
    def dataInputAlias(self):
        return self._data_input_alias

    @dataInputAlias.setter
    def dataInputAlias(self, value):
        self._data_input_alias = value

    @property
    def moveData(self):
        return self._move_data

    @moveData.setter
    def moveData(self, value):
        self._move_data = value

    @property
    def updateInputAlias(self):
        return self._update_input_alias

    @updateInputAlias.setter
    def updateInputAlias(self, value):
        self._update_input_alias = value

    def template(self):
        """Create an IndexTemplate and save it into elasticsearch."""
        index_template = self._dsl_document._index.as_template(template_name=self._template_name, pattern=self._index_pattern)
        index_template.save()

        self.create_and_migrate()

        return

    def create_and_migrate(self, _index_id=1):
        """
        Upgrade function that creates a new index for the data. Optionally it also can
        (and by default will) reindex previous copy of the data into the new index
        (specify ``move_data=False`` to skip this step) and update the alias to
        point to the latest index (set ``update_alias=False`` to skip).
        Note that while this function is running the application can still perform
        any and all searrches without any loss of functionality. It should, however,
        not perform any writes at this time as those might be lost.
        """

        # get the low level connection
        self._es = connections.get_connection()

        # Get the largest Index number that exists and add one to it for the new index
        _es_last_index = 0
        _previous_index = ""
        for index in self._es.indices.get(self._index_pattern):
            _index_number = int(index.split("-")[-1])
            if _index_number >= _es_last_index:
                _previous_index = index
                _es_last_index = _index_number

        _index_id = _es_last_index + 1
        _index_number = str(_index_id).zfill(6)

        # construct a new index name by appending current timestamp
        _next_index = self._index_pattern.replace("*", _index_number)

        # create new index, it will use the settings from the template
        self._es.indices.create(index=_next_index)

        if self._move_data:
            # move data from current alias to the new index
            self._es.reindex(
                body={"source": {"index": _previous_index}, "dest": {"index": _next_index}},
                request_timeout=3600,
            )
            # refresh the index to make the changes visible
            self._es.indices.refresh(index=_next_index)

        if self._update_input_alias and self._data_input_alias and _previous_index:
            # repoint the data input alias to point to the newly created index
            self._es.indices.update_aliases(
                body={
                    "actions": [
                        {"remove": {"alias": self._data_input_alias, "index": _previous_index}},
                        {"add": {"alias": self._data_input_alias, "index": _next_index}},
                    ]
                }
            )
        elif self._update_input_alias and self._data_input_alias and not _previous_index:
            self._es.indices.update_aliases(
                body={
                    "actions": [
                        {"add": {"alias": self._data_input_alias, "index": _next_index}},
                    ]
                }
            )

        return


if __name__ == "__main__":
    ES_CONNECTION = {}
    ES_CONNECTION["hosts"] = "https://98a8d377ae5e443b93c663ea55575976.eu-west-1.aws.found.io/"
    ES_CONNECTION["http_auth"] = ("elastic", "WFZjLsJmQ52qzcfkuDxQbgpk")
    ES_CONNECTION["scheme"] = "https"
    ES_CONNECTION["timeout"] = 60
    ES_CONNECTION["port"] = 9243
    ES_CONNECTION["verify_certs"] = True

    # initiate the default connection to elasticsearch
    connections.create_connection(**ES_CONNECTION, ca_certs=certifi.where())

    # create the empty index
    es_index_manage = manageESIndex()
    es_index_manage.dslDocument = TEAMS
    es_index_manage.templateName = TEMPLATE_NAME
    es_index_manage.indexPattern = PATTERN
    es_index_manage.dataInputAlias = DataInput.alias
    es_index_manage.template()
