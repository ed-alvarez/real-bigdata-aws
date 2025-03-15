"""
High level elasticsearch DSL
"""
import logging

from elasticsearch import exceptions
from elasticsearch_dsl import Document

from shared.shared_src.es.es_client import ElasticSearchClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ESUploadDSl:
    def __init__(self, es_client: ElasticSearchClient):
        self.es_client_obj = es_client
        self._document = Document

    def get_es_client(self):
        logger.debug(f"Get ES Client Connection for {self.es_client_obj}")
        try:
            raw_es_client = self.es_client_obj.get_client()
        except exceptions.ElasticsearchException as exception:
            logger.exception(f"ElasticSearch Connection Failed {exception}")
            raise
        return raw_es_client

    def insert_document(self, document: Document, obj_id: str, index_table: str, es_id: str = "", es_type: str = ""):
        response = {}
        logger.debug(f"Pushing ES DSL {document.to_dict()} ")
        logger.info(f"ID {obj_id} into {index_table} with {es_type}---")

        logger.debug("Get Connection")
        raw_es_connection = self.get_es_client()

        logger.debug("Upload Document")
        # Have removed the id_setting as getting conflicts in uploads.  Will use underlying ES ID's for now

        try:
            response = document.save(using=raw_es_connection, index=index_table, op_type=es_type)
            logger.info(f"Success: Upsert {document} ID {obj_id}---")
        except Exception as ex:
            logger.error(f"Elastic DSL Client upsert error {ex}")
            raise
        logger.info(response)
        return response
