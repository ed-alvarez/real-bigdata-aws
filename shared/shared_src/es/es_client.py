"""
Elasticsearch client
"""

import logging
from typing import Any, Iterable

from elasticsearch import Elasticsearch, exceptions

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ElasticSearchClient:
    def __init__(self, ES_PASSWORD: str, ES_USER: str, ES_CLOUD_ID: str):
        """
        __init__() is not in charge of creating the client but self.get_client()
        """
        self._es_pass = ES_PASSWORD
        self._es_user = ES_USER
        self._es_cloud_id = ES_CLOUD_ID
        self.es_client = None

    def get_client(self):
        """
        Returns Elasticsearch client, if not exist then create a new client
        """
        if self.es_client:
            return self.es_client
        try:
            logger.debug(f"Connecting to ElasticSearch - {self._es_cloud_id}, User: {self._es_user}, Password: {self._es_pass}")
            self.es_client = Elasticsearch(cloud_id=self._es_cloud_id, http_auth=(self._es_user, self._es_pass))
            logger.debug(f"Ping Elastic Cloud {self._es_cloud_id}")
            logger.info(f"ElasticSearch Connection succeeded {self.es_client.ping()}")
            logger.debug(f"ElasticSearch Client Cloud ID: {self._es_cloud_id}")
        except exceptions.ElasticsearchException as exception:
            logger.exception(f"ElasticSearch Connection Failed {exception}")
        return self.es_client

    def check_cluster_health(self):
        try:
            health = self.get_client().cluster.health(request_timeout=30)
            return health
        except Exception as error:
            logging.error(f"Error on Cluster check! {error}")

    def create_index(self, index_name: str):
        self.get_client().indices.create(index=index_name, ignore=400)

    def delete_index(self, index_name: str):
        self.get_client().indices.delete(index=index_name)

    def get_all_indexes(self, template_name: str):
        return self.get_client().indices.get_template(template_name)

    def get_all_indexes(self) -> Iterable[Any]:
        yield from self.get_client().indices.get_alias().keys()

    def get_all_index_rows(self, index_name: str):
        return self.get_client().search(index=index_name, query={"match_all": {}})

    def bulk_insert_data_to_es(self, data, index, bulk_size=100):
        try:
            batch_data = self.get_list_by_chunk_size(data, bulk_size)
            for batch in batch_data:
                count = 0
                actions = []
                while count <= len(batch) - 1:
                    action = {"_index": index, "_source": batch[count]}
                    actions.append(action)
                    count += 1
            return True
        except Exception as error:
            logger.error(f"Bulk insertion job failed {error}")
            return False

    @staticmethod
    def get_list_by_chunk_size(original_list, batch_size):
        # looping length equals batch_size
        for count in range(0, len(original_list), batch_size):
            yield original_list[count : count + batch_size]
