from elasticsearch_dsl import CustomField, Document, connections
from email_helpers.es_index_management import manageESIndex

VERSION_NUMBER = 1
TEMPLATE_NAME = "ips-test-date-v" + str(VERSION_NUMBER)
PATTERN = TEMPLATE_NAME + "-*"


class Schema:
    """Increment this number for each change rolled into production"""

    version = VERSION_NUMBER


class DataInput:
    alias = "ips_date_input"


class fingerprintDate(CustomField):
    builtin_type = "date"

    "2020-09-25 15:44:47.514592"

    def _serialize(self, data):
        return data.strftime("%Y-%m-%d %H:%M:%S")


class TESTDATE(Document):
    new_date = fingerprintDate(format="yyyy-MM-dd HH:mm:ss")


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
    es_index_manage.dslDocument = TESTDATE
    es_index_manage.templateName = TEMPLATE_NAME
    es_index_manage.indexPattern = PATTERN
    es_index_manage.dataInputAlias = DataInput.alias
    es_index_manage.template()
