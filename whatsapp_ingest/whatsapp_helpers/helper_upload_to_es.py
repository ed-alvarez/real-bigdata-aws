# coding=utf-8
import logging
import sys

from elasticsearch_dsl import Document, connections

from whatsapp_ingest import whatsapp_settings as settings
from whatsapp_ingest.whatsapp_helpers.es_whatsapp_index import WHATSAPP

log = logging.getLogger()


class UploadToElasticsearch:
    def __init__(self):
        self._whatsapp_obj: Document = WHATSAPP()
        self._es_id = None
        try:
            connections.create_connection(**settings.ES_CONNECTION)
        except Exception as ex:
            error_type, error_instance, traceback = sys.exc_info()
            log.exception(ex)
            raise error_type(error_instance.info).with_traceback(traceback)

    @property
    def whatsappObj(self):
        return self._whatsapp_obj

    @whatsappObj.setter
    def whatsappObj(self, whatsapp_obj: Document):
        self._whatsapp_obj = whatsapp_obj
        log.debug(f"generate ESID with {self._whatsapp_obj.fingerprint.ses_message_id}")
        self._es_id = self._whatsapp_obj.fingerprint.ses_message_id
        log.debug(f"ESID = {self._es_id}")

    def do_upload(self):
        response = None
        try:
            response = self._whatsapp_obj.save(refresh=True, index=settings.INPUT_INDEX, id=self._es_id, op_type=settings.ES_OP_TYPE)
        except Exception as ex:
            if ex.status_code == 409:
                warning_msg = f"{self.__class__.__name__} : es_document_already_exists: {ex}"
                log.warning(warning_msg)
                raise Exception(warning_msg)
                pass
            else:
                error_type, error_instance, traceback = sys.exc_info()
                log.error(ex)
                raise error_type(error_instance.info).with_traceback(traceback)

        log.info(response)
