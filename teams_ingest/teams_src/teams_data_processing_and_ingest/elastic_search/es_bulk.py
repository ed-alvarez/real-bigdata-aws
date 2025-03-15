import logging
import sys
from pathlib import Path
from typing import Dict, List

tenant_directory = Path(__file__).resolve().parent.parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))

import certifi
from elasticsearch import Elasticsearch, exceptions, helpers
from teams_settings import ES_CLOUD_ID, ES_INDEX, ES_OP_TYPE, ES_PASSWORD, ES_USER
from teams_src.teams_data_processing_and_ingest.message_es_bulk_object import (
    TeamsBulkMessages,
)

from shared.shared_src.es.es_client import ElasticSearchClient

log = logging.getLogger()


class esBulk:
    def __init__(self) -> None:
        super().__init__()
        self._es_connection: Elasticsearch = ElasticSearchClient(ES_PASSWORD, ES_USER, ES_CLOUD_ID).get_client()

    def _convert_data_to_es_bulk(self, es_bulk_data: TeamsBulkMessages) -> List[Dict]:
        raise NotImplementedError()

    def upload_data(self, es_bulk_data: TeamsBulkMessages) -> None:

        try:
            successes, errors = helpers.bulk(
                client=self._es_connection,
                actions=self._convert_data_to_es_bulk(es_bulk_data=es_bulk_data),
                chunk_size=500,
                request_timeout=500,
                max_retries=3,
                initial_backoff=20,
                max_backoff=600,
                raise_on_error=True,
                raise_on_exception=False,
            )

            if successes:
                log.info(f"Bulk request finished, successfully sent {successes} records")

            for fail in errors:
                fail_info: Dict = fail["index"]
                fail_id: str = fail_info["_id"]
                fail_index: str = fail_info["_index"]
                fail_error_type: str = fail_info["error"]["type"]
                fail_error_reason: str = fail_info["error"]["reason"]
                error_message: str = f"{fail_error_type} in {fail_id}, uploading to {fail_index} because {fail_error_reason}"
                log.exception(error_message)

        except exceptions.ElasticsearchException as ex:
            error_reason: str = ex.errors[0]["index"]["error"]["reason"]
            log.info(f"Bulk Upload erroring out of: {error_reason}")
            log.exception(error_reason)
            raise exceptions.ElasticsearchException(error_reason)


class TEAMS_esBulk(esBulk):
    def __init__(self) -> None:
        super().__init__()

    def _convert_data_to_es_bulk(self, es_bulk_data: TeamsBulkMessages) -> List[Dict]:
        log.debug("Converting teams_conversation object to ES Bulk format")
        es_record: Dict = {}
        es_record["_index"]: str = ES_INDEX
        es_record["_op_type"]: str = ES_OP_TYPE

        bulk_data: List[Dict] = []
        record: Dict
        for record in es_bulk_data.listOfConversationItems:
            # Use a consistent ES ID
            es_record["_id"]: str = f'{record["conversationid"]}-{record["messageid"]}'
            # Populate the source with relevant Data
            es_record["_source"]: Dict = record
            bulk_data.append(es_record.copy())

        return bulk_data
