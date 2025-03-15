#!/usr/bin/env python

""" Module providing functions for ElasticSearch document and sub-object creation """
import copy
import functools
from datetime import datetime
from typing import Iterable, List

import es_schema.es_slack_index as ess
import helpers.es_slack_id
import helpers.s3


def _create_fingerprint_meta_inner_doc(
    client_name: str, message_dt: datetime, channel_label: str, s3: helpers.s3.S3
) -> ess.FingerprintMeta:

    processed_key = s3.get_processed_s3_key_for_slack_messages_by_channel_label(channel_label)

    conversation_type = "slack"

    fpm = ess.FingerprintMeta(
        bucket=f"{client_name}.ips",
        client=client_name,
        time=message_dt,
        type=conversation_type,
        processed_time=datetime.now(),
        schema=ess.VERSION_NUMBER,
        key=processed_key,
    )
    return fpm


def _create_item_id_inner_doc(item_date: datetime, item_number: int, channel_id: str, client_name: str) -> ess.ItemId:
    """ "item_id" : {
      "item_date" : "210119",
      "item_id" : "0x2000001D86C55",
      "item_number" : "1284",
      "es_id" : "0x2000001D86C552101191284"
    },
    """
    yymmdd = item_date.strftime("%y%m%d")
    es_id = f"{client_name}-{channel_id}-{yymmdd}-{item_number}"
    ii = ess.ItemId(
        item_date=yymmdd,
        item_id=f"{client_name}-{channel_id}",
        item_number=item_number,
        es_id=es_id,
    )
    return ii


def _create_body_detail_inner_doc(body_text: str, sentiment_inner_doc: ess.Sentiment) -> ess.BodyDetail:
    len_b = len(body_text)
    bd = ess.BodyDetail()
    bd.has_body = len_b > 0
    bd.body_size = len_b
    bd.body_sentiment = sentiment_inner_doc
    return bd


def _create_sentiment_inner_doc(sentiment: dict) -> ess.Sentiment:
    s = ess.Sentiment(**sentiment)  # Unpacks dictionary and populates keys as class members
    return s


@functools.lru_cache(maxsize=8192)
def _create_slack_id_summary(
    slack_id: str,
    esiidc: helpers.es_slack_id.SlackIdInnerDocCreator,
) -> str:
    sis = esiidc.get_slack_id_inner_doc(slack_id)
    return f"{sis.fullname} <{sis.emailaddress}>"


@functools.lru_cache(maxsize=8192)
def __create_slack_id_summaries_cached(slack_ids: frozenset, esiidc: helpers.es_slack_id.SlackIdInnerDocCreator) -> List[str]:
    siss = _create_slack_id_inner_docs(slack_ids, esiidc)
    return sorted([f"{sis.fullname} <{sis.emailaddress}>" for sis in siss])


@functools.lru_cache(maxsize=8192)
def __create_slack_id_inner_docs_cached(slack_ids: frozenset, esiidc: helpers.es_slack_id.SlackIdInnerDocCreator) -> List[ess.SlackId]:
    unsorted = [esiidc.get_slack_id_inner_doc(slack_id) for slack_id in slack_ids]
    return sorted(unsorted, key=lambda x: x.fullname)


def _create_slack_id_summaries(slack_ids: Iterable, esiidc: helpers.es_slack_id.SlackIdInnerDocCreator) -> List[str]:
    return __create_slack_id_summaries_cached(frozenset(slack_ids), esiidc)


def _create_slack_id_inner_docs(slack_ids: Iterable, esiidc: helpers.es_slack_id.SlackIdInnerDocCreator) -> List[ess.SlackId]:
    return __create_slack_id_inner_docs_cached(frozenset(slack_ids), esiidc)


def create_es_attachment_slack_document(
    file_slack_id: str,
    filename: str,
    file_size: str,
    text: str,
    error: str,
    processed_s3_path: str,
    parent_message: dict,
    client_name: str,
    s3_helper: helpers.s3.S3,
    message_number,
    channel_id: str,
    channel_label,
    channels: dict,
    users: dict,
    es_slack_id_inner_doc_creator: helpers.es_slack_id.SlackIdInnerDocCreator,
) -> ess.SlackDocument:
    """
    Attachment
    filename = Keyword()
    content = Text(analyzer='english', term_vector='with_positions_offsets')
    filesize = Integer()
    error = Text()
    tar_file_location = Text()
    fileid = Keyword()
    """
    attachment_inner_doc = ess.Attachment(
        filename=filename,
        content=text,
        filesize=file_size,
        error=error,
        tar_file_location=processed_s3_path,
        fileid=file_slack_id,
    )

    # make sure we don't alter original message, even if it should be ok
    attachment_message = copy.deepcopy(parent_message)
    attachment_message["text"] = ""
    attachment_message["sentiment"] = {}

    sd = create_es_slack_document(
        attachment_message,
        client_name,
        s3_helper,
        message_number,
        channel_id,
        channel_label,
        channels,
        users,
        es_slack_id_inner_doc_creator,
    )

    # replace sentiment with sentiment of attachment content <-- not doing attachment sentiment in bbg/email
    # sd.body_detail.sentiment = {}

    # Populate attachment object
    sd.attachments = [attachment_inner_doc]  # This is a list of one in BB and Email parse

    return sd


def create_es_slack_document(
    message: dict,
    client_name: str,
    s3_helper: helpers.s3.S3,
    message_number,
    channel_id: str,
    channel_label,
    channels: dict,
    users: dict,
    es_slack_id_inner_doc_creator: helpers.es_slack_id.SlackIdInnerDocCreator,
) -> ess.SlackDocument:
    sd = ess.SlackDocument()
    sd.datetime = message["datetime"]
    # sd.attachments
    sd.conversationid = f"{client_name}.{channel_id}"
    sd.fingerprint = _create_fingerprint_meta_inner_doc(client_name, message["datetime"], channel_label, s3_helper)
    sd.from_ = _create_slack_id_summary(message["from"], es_slack_id_inner_doc_creator)
    sd.from_detail = es_slack_id_inner_doc_creator.get_slack_id_inner_doc(message["from"])
    sd.datetimeutc = message["datetimeutc"]
    sd.to = _create_slack_id_summaries(message["to"], es_slack_id_inner_doc_creator)
    sd.to_detail = _create_slack_id_inner_docs(message["to"], es_slack_id_inner_doc_creator)
    sd.body = message["text"]
    sentiment_inner_doc = _create_sentiment_inner_doc(message["sentiment"])
    sd.body_detail = _create_body_detail_inner_doc(message["text"], sentiment_inner_doc)
    sd.item_id = _create_item_id_inner_doc(message["datetime"], message_number, channel_id, client_name)
    sd.ts = message["ts"]
    if "thread_ts" in message:
        sd.thread_ts = message["thread_ts"]
    return sd
