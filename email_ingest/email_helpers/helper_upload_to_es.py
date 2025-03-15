# coding=utf-8
import logging

import email_settings
from elasticsearch.exceptions import ConflictError
from elasticsearch_dsl import connections
from email_helpers.es_email_index_v2 import EMAIL
from email_helpers.log_messages import warning

log = logging.getLogger()


class UploadToElasticsearch:
    def __init__(self):
        self._email_dict = EMAIL()
        self._es_id = None
        try:
            connections.create_connection(**email_settings.ES_CONNECTION)
        except Exception as err:
            log.exception(err)
            raise AttributeError(err)

    @property
    def emailDict(self):
        return self._email_dict

    @emailDict.setter
    def emailDict(self, email_dict):
        self._email_dict = email_dict
        log.debug(f"{self._email_dict.to_dict(include_meta=True)}")

        # If this is run in history mode take the ID from the file name which will be the SES ID
        file_name = self._email_dict.fingerprint.key.rsplit("/", 1)[1]
        log.debug(f"generate ESID with {file_name}")
        self._es_id = file_name

    @property
    def esId(self):
        return self._es_id

    @esId.setter
    def esId(self, es_id):
        self._es_id = es_id
        log.debug(f"ESID = {self._es_id}")

    def do_upload(self):
        if self._es_id:
            response = None

            try:
                response = self._email_dict.save(
                    refresh=True,
                    index=email_settings.INPUT_INDEX,
                    id=self._es_id,
                    op_type=email_settings.ES_OP_TYPE,
                )
            except Exception as ex:
                if ex.status_code == 409:
                    warning_msg = warning["es_document_already_exists"].format(ex)
                    log.warning(warning_msg)
                    raise ConflictError()
                else:
                    log.error(ex)
                    raise Exception(ex)
            log.info(response)
            return response
        else:
            log.error("No ESID Set")
            raise ValueError("No ESID Set")
