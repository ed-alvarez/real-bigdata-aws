import json
import logging

import certifi
from bbg_settings import ES_CONNECTION, LOCAL_TIKA
from elasticsearch import Elasticsearch, exceptions, helpers

log = logging.getLogger()


class esBulk:
    def __init__(self):

        self._es_url = str()
        self._es_hostname = str()
        self._es_port = str()
        self._es_user = str()
        self._es_password = str()

        self._bulk_data_list = list()
        self._bulk_data_json = list()
        self._es_index = str()
        self._es_pipeline = str()

        _es_connection_string = str()

    @property
    def esIndex(self):
        return self._es_index

    @esIndex.setter
    def esIndex(self, es_index):
        self._es_index = es_index
        log.info(f"Writing bulk data to {es_index}")

    @property
    def esPipeline(self):
        return self._es_pipeline

    @esPipeline.setter
    def esPipeline(self, es_pipeline):
        self._es_pipeline = es_pipeline

    @property
    def esBulkData(self):
        return self._bulk_data_list

    @esBulkData.setter
    def esBulkData(self, bulk_data_list):
        self._bulk_data_list = bulk_data_list

    def set_parameters(self):
        self._es_url = ES_CONNECTION["scheme"]
        self._es_hostname = ES_CONNECTION["hosts"]
        self._es_port = str(ES_CONNECTION["port"])
        self._es_user = ES_CONNECTION["http_auth"][0]
        self._es_password = ES_CONNECTION["http_auth"][1]

        _es_connection_string = (
            self._es_url + "://" + self._es_user + ":" + self._es_password + "@" + self._es_hostname + ":" + self._es_port
        )
        log.debug("Connecting to: %s", _es_connection_string)
        try:
            log.debug("Initialising ElasticSearch Connection...")
            self.es = Elasticsearch(_es_connection_string, ca_certs=certifi.where())
            log.info("ElasticSearch connection succeeded. %s", self.es)

        except exceptions.ElasticsearchException as ex:
            log.exception("ElasticSearch Connection Failed %s", ex)
            raise ex
        return

    def upload_data(self):
        try:
            successes, errors = helpers.bulk(
                client=self.es,
                actions=self._bulk_data_json,
                chunk_size=500,
                request_timeout=600,
                max_retries=3,
                initial_backoff=20,
                max_backoff=600,
                raise_on_error=True,
                raise_on_exception=False,
            )

            if successes:
                log.info("Bulk request finished, successfully sent %d operations", successes)

            for fail in errors:
                fail_info = fail["index"]
                fail_id = fail_info["_id"]
                fail_index = fail_info["_index"]
                fail_error_type = fail_info["error"]["type"]
                fail_error_reason = fail_info["error"]["reason"]
                error_message = f"{fail_error_type} in {fail_id}, uploading to {fail_index} because {fail_error_reason}"
                log.exception(error_message)

        except exceptions.ElasticsearchException as ex:
            error_reason = ex.errors[0]["index"]["error"]["reason"]
            log.exception(str(error_reason))
            raise exceptions.ElasticsearchException(error_reason)


class IB_esBulk(esBulk):
    def convert_data_to_es_bulk(self):
        log.debug("Converting bbg_ib_conversation to ES Bulk format")
        es_record = dict()
        es_record["_index"] = self._es_index
        es_record["_op_type"] = "index"

        bulk_data = list()
        for record in self._bulk_data_list:
            # Use a pipeline if there is an attachment
            if not LOCAL_TIKA:
                if "attachments" in record:
                    # Special case.  If there is only 1 attachment and it's an error don't pipeline it
                    # this happens for bbg im
                    if len(record["attachments"]) == 1:
                        if not "error" in record["attachments"][0]:
                            es_record["pipeline"] = self._es_pipeline
                    else:
                        es_record["pipeline"] = self._es_pipeline
                else:
                    es_record.pop("pipeline", None)
            # Use a consistent ES ID
            es_record["_id"] = record["item_id"]["es_id"]
            # Populate the source with relevant Data
            es_record["_source"] = record

            bulk_data.append(es_record.copy())

        self._bulk_data_json = bulk_data


class MSG_esBulk(esBulk):
    def convert_data_to_es_bulk(self):
        es_record = dict()
        es_record["_index"] = self._es_index
        es_record["_op_type"] = "index"

        bulk_data = list()
        for record in self._bulk_data_list:
            # Use a pipeline if there is an attachment
            if not LOCAL_TIKA:
                if "attachments" in record:
                    # Special case.  If there is only 1 attachment and it's an error don't pipeline it
                    # this happens for bbg im
                    if len(record["attachments"]) == 1:
                        if not "error" in record["attachments"][0]:
                            es_record["pipeline"] = self._es_pipeline
                    else:
                        es_record["pipeline"] = self._es_pipeline
                else:
                    es_record.pop("pipeline", None)
            # Use a consistent ES ID
            es_id = record.pop("es_id") + "-" + record["msgtimeutc"] + "-" + record["fingerprint"]["client"]
            es_record["_id"] = es_id
            # Populate the source with relevant Data
            es_record["_source"] = record

            bulk_data.append(es_record.copy())

        self._bulk_data_json = bulk_data


if __name__ == "__main__":

    esobj = esBulk(es_index="bbg-parse-msg-test", es_pipeline="bbg-msg-parse")
    with open("/Users/hogbinj/Documents/GitHub/bbg-parse/TestData/large_password.json") as json_file:
        records = list()
        data = json.loads(json_file.read())
        records.append(data)
        esobj.add_data(bulk_data_dict=records)
        esobj.upload_data()
