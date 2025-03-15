# coding=utf-8
from logging import getLogger

from elasticsearch_dsl import connections
from voice_settings import ES_CONNECTION, ES_OP_TYPE, INPUT_INDEX
from voice_src.process_transcript_job.elastic_search.es_voice_index_v1 import VOICE

log = getLogger()


class UploadToElasticsearch:
    def __init__(self):
        self._voice_dict = VOICE()
        self._es_id = None
        try:
            connections.create_connection(**ES_CONNECTION)
        except Exception as err:
            log.exception(err)
            raise AttributeError(err)

    @property
    def voiceDict(self):
        return self._voice_dict

    @voiceDict.setter
    def voiceDict(self, email_dict):
        self._voice_dict = email_dict
        # log.debug(f'{self._voice_dict.to_dict(include_meta=True)}')

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
                response = self._voice_dict.save(refresh=True, index=INPUT_INDEX, id=self._es_id, op_type=ES_OP_TYPE)
            except Exception as ex:
                if ex.status_code == 409:
                    warning_msg = "es_document_already_exists"
                    log.warning(warning_msg)
                    raise Exception(warning_msg)
                    pass
                else:
                    log.error(ex)
                    raise Exception(ex)
            log.info(response)
            return response
        else:
            log.error("No ESID Set")
            raise ValueError("No ESID Set")
