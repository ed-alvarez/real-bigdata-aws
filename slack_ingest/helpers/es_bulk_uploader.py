import logging
from typing import List

import certifi
import elasticsearch
import es_schema.es_slack_index as ess
import settings

log = logging.getLogger()


def _get_bulk_format_dicts_from_es_docs(es_index, docs: List[ess.SlackDocument]) -> List[dict]:
    log.debug("Converting ES docs to ES Bulk format")
    bulk_format_list = []
    for doc in docs:
        record = doc.to_dict()
        es_record = {
            "_index": es_index,
            "_op_type": "index",
            # Use a consistent ES ID
            "_id": record["item_id"]["es_id"],
            "_source": record,
        }
        bulk_format_list.append(es_record)
    return bulk_format_list


class ESBulkUploader:
    def __init__(self):
        self.es_index = ess.DataInput.alias  # settings.SOMETHING in email/bbg

        es_scheme_protocol = settings.ES_CONNECTION["scheme"]
        es_hostname = settings.ES_CONNECTION["hosts"]
        es_port = str(settings.ES_CONNECTION["port"])
        es_user = settings.ES_CONNECTION["http_auth"][0]
        es_password = settings.ES_CONNECTION["http_auth"][1]

        es_connection_string = f"{es_scheme_protocol}://{es_user}:{es_password}@{es_hostname}:{es_port}"
        log.debug("Connecting to: %s", es_connection_string)
        try:
            log.debug("Initialising ElasticSearch Connection...")
            self.es = elasticsearch.Elasticsearch(es_connection_string, ca_certs=certifi.where())
            log.info("ElasticSearch connection succeeded. %s", self.es)

        except elasticsearch.exceptions.ElasticsearchException as ex:
            log.exception("ElasticSearch Connection Failed %s", ex)
            raise ex

    def upload_docs(self, docs: List[ess.SlackDocument]):
        bulk_format_dicts = _get_bulk_format_dicts_from_es_docs(self.es_index, docs)
        log.info("Do bulk import to ElasticSearch")
        try:
            successes, errors = elasticsearch.helpers.bulk(
                client=self.es,
                actions=bulk_format_dicts,
                chunk_size=500,
                request_timeout=500,
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

        except elasticsearch.exceptions.ElasticsearchException as ex:
            # error_reason = ex.errors[0]['index']['error']['reason']
            log.exception(str(ex))
            raise elasticsearch.exceptions.ElasticsearchException(ex)

        return bulk_format_dicts  # Return list to be persisted as json in S3 processed folder
