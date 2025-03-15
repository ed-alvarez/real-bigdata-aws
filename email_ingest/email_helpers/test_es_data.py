from datetime import datetime

from elasticsearch_dsl import connections

from email_ingest.email_helpers.test_es_serializer import TESTDATE


class DoTheTestDate:
    def __init__(self):
        self._test_date = TESTDATE()
        try:
            stage = "dev"
            ES_HOST = dict()
            ES_PASSWORD = dict()
            ES_HOST["dev"] = "98a8d377ae5e443b93c663ea55575976.eu-west-1.aws.found.io"
            ES_PASSWORD["dev"] = "WFZjLsJmQ52qzcfkuDxQbgpk"

            es_host = ES_HOST[stage]
            es_password = ES_PASSWORD[stage]

            connections.create_connection(hosts=[es_host], http_auth=("elastic", es_password), scheme="https", timeout=60, port=9243)
        except Exception as err:
            raise AttributeError(err)

    def populate_es_record(self):
        self._test_date.date = datetime.now()
        self._test_date.new_date = datetime.now()

    def populate(self):
        response = None

        try:
            response = self._test_date.save(index="ips-test-date-v1-000001")
        except Exception as ex:
            print(ex)
            raise Exception(ex)

        print(response)
        return response


test_obj = DoTheTestDate()
test_obj.populate_es_record()
response = test_obj.populate()
print(response)
