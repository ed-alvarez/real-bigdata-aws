"""
Helper functions for item_id creation
"""
import logging
from datetime import datetime

from bbg_helpers.es_bbg_ib_index import BBG_IB
from bbg_helpers.es_bbg_ib_index import item_id as es_item_id
from bbg_src.ib_upload_lambda.ib_upload_settings import ESField

log = logging.getLogger()


def _conversation_id_part(conversation_id: str) -> str:
    conversation_id_part: str = conversation_id.split("-")[1]
    if ":" in conversation_id_part:
        new_conversation_id_part: str = conversation_id_part.split(":")[1]
        return new_conversation_id_part
    return conversation_id_part


def generate_item_id(ibMessage: BBG_IB, messageNumber: int) -> es_item_id:
    item_id: es_item_id = es_item_id()
    conversation_date_seconds: int = int()

    conversation_es_id_part: str = _conversation_id_part(conversation_id=ibMessage.conversationid)

    try:
        conversation_date_seconds = int(ibMessage.datetimeutc)
    except Exception as ex:
        log.exception(ex)
        print(ex)

    conversation_es_id_date: str = str(datetime.fromtimestamp(conversation_date_seconds).strftime("%y%m%d"))

    item_id.item_id = conversation_es_id_part
    item_id.item_date = conversation_es_id_date
    item_id.item_number = str(messageNumber)
    item_id.es_id = "".join([conversation_es_id_part, conversation_es_id_date, str(messageNumber)])

    return item_id
