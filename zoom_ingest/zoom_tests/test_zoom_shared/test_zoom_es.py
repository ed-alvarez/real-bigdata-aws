"""
Test for Elasticsearch client & DSL
"""
import datetime
from contextlib import contextmanager
from typing import Iterable

import pytest
from elasticsearch_dsl import Document, Object

from shared.shared_src.es.es_client import ElasticSearchClient
from shared.shared_src.es.es_dsl_client import ESUploadDSl
from zoom_ingest.zoom_shared.zoom_es_models import FingerprintMeta
from zoom_ingest.zoom_shared.zoom_es_parser import parser_blob_to_es_docs

# TODO: give love


def test_client_creation_only_once():
    elasticsearch_client = ElasticSearchClient(host="http://localhost:9200")
    client_1 = elasticsearch_client.get_client()
    client_2 = elasticsearch_client.get_client()
    assert id(client_1) == id(client_2)


def test_create_index():
    index_name = "my_test_index"
    elasticsearch_client = ElasticSearchClient(host="http://localhost:9200")
    indexes = elasticsearch_client.get_all_indexes()
    assert index_name in indexes


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize(
    "index_name, expectation ",
    [
        (".tasks", does_not_raise()),
        ("goo", pytest.raises(Exception)),
    ],
)
def test_get_all_index_rows(index_name, expectation):
    elasticsearch_client = ElasticSearchClient(host="http://localhost:9200")
    with expectation:
        response = elasticsearch_client.get_all_index_rows(index_name)
        assert response is not None


@pytest.mark.parametrize(
    "index_name, fingerprint",
    [
        (
            "fingerprint",
            FingerprintMeta(
                bucket="",
                client="",
                key_audio="",
                key_cdr="",
                key_transcript="",
                processed_time=datetime.now(),
                time=datetime.now(),
                tenant="",
                type_source="",
                type_transcription="",
                aws_lambda_id="",
                schema="",
            ),
        ),
    ],
)
def test_dsl_save_fingerprint_meta_document(index_name, fingerprint):
    class EmptyDocument(Document):
        """Since InnerDOc is only for nested fields, we need to create a dummy document"""

        fingerprint = Object(FingerprintMeta)

    elasticsearch_client = ElasticSearchClient(host="http://localhost:9200")
    elasticsearch_client.delete_index(
        index_name=index_name,
        ignore_unavailable=True,
    )
    dsl = ESUploadDSl(elasticsearch_client)
    doc = EmptyDocument(fingerprint=fingerprint)
    insert_response = dsl.insert_document(document=doc, index_table=index_name)
    assert insert_response == "created"
    search_response: Iterable = dsl.search(index_name)
    for response in search_response:
        assert response.fingerprint["bucket"] == fingerprint.bucket
        assert response.fingerprint["client"] == fingerprint.client
        assert response.fingerprint["key_audio"] == fingerprint.key_audio
        assert response.fingerprint["key_cdr"] == fingerprint.key_cdr
        assert response.fingerprint["key_transcript"] == fingerprint.key_transcript
        assert response.fingerprint["processed_time"] == datetime.strftime(
            fingerprint.processed_time,
            "%Y-%m-%d %H:%M:%S",
        )
        assert response.fingerprint["time"] == datetime.strftime(
            fingerprint.time,
            "%Y-%m-%d %H:%M:%S",
        )
        assert response.fingerprint["tenant"] == fingerprint.tenant
        assert response.fingerprint["type_source"] == fingerprint.type_source
        assert response.fingerprint["type_transcription"] == fingerprint.type_transcription
        assert response.fingerprint["aws_lambda_id"] == fingerprint.aws_lambda_id
        assert response.fingerprint["schema"] == fingerprint.schema


def test_parser_blob_to_es_docs():
    data = {
        "zoom_event": {"source_id": 87030098067},
        "cdr": {
            "origin": "XD5VZiZVTMCrBnaw7Dw0iw",
            "destination": [
                {
                    "id": "Zf5WmbD-Ta21qliPoendNg",
                    "name": "Can Ozdemir",
                    "user_email": "can.ozdemir@melqart.com",
                },
                {
                    "id": "Zmhw6HHBSeOTM4iWF_jjbg",
                    "name": "Steve Platts",
                    "user_email": "steve.platts@melqart.com",
                },
                {
                    "id": "Zmhw6HHBSeOTM4iWF_jjbg",
                    "name": "Steve Platts",
                    "user_email": "steve.platts@melqart.com",
                },
                {
                    "id": "QCMTSUQBQHesnflm6p_I4A",
                    "name": "Joseph Gebran",
                    "user_email": "joseph.gebran@melqart.com",
                },
            ],
            "date_of_action": "2022-08-05T08:26:08Z",
            "source_type": "meeting",
        },
        "transcript": {
            "type": "M4A",
            "recording_id": "ca5de797-163c-4aef-b846-3b90e776a123",
            "start_time": "2022-08-05T08:26:09Z",
            "end_time": "2022-08-05T08:49:18Z",
            "content": [
                {
                    "text": "Grad school here hey man.",
                    "end_ts": "00:00:07.290",
                    "ts": "00:00:06.180",
                    "users": [
                        {
                            "username": "442070814383",
                            "multiple_people": False,
                            "user_id": "442070814383",
                            "zoom_userid": "Unknown Speaker",
                            "client_type": 0,
                        },
                    ],
                },
                {
                    "text": "hey.",
                    "end_ts": "00:00:09.090",
                    "ts": "00:00:08.490",
                    "users": [
                        {
                            "username": "Ghislain Cortina",
                            "multiple_people": False,
                            "user_id": "49555532639965566835",
                            "zoom_userid": "w7T_zz-kSOaDKTpqfqKLhA",
                            "client_type": 0,
                        },
                    ],
                },
            ],
        },
        "recording": {
            "recording_id": "ca5de797-163c-4aef-b846-3b90e776a123",
            "play_url": "https://melqart.zoom.us/rec/play/u0lxMmfwYrxkgBgMAZK_F_GclpIjlUwiGsGHSQbzbrwWPLRqolD5rDN8zD1rQ6_zBhDjJJW9IDBggahW.XIw1Z42P-xH6WcSa",
            "download_url": "https://melqart.zoom.us/rec/download/u0lxMmfwYrxkgBgMAZK_F_GclpIjlUwiGsGHSQbzbrwWPLRqolD5rDN8zD1rQ6_zBhDjJJW9IDBggahW.XIw1Z42P-xH6WcSa",
        },
    }
    elasticsearch_client = ElasticSearchClient(host="http://localhost:9200")
    dsl = ESUploadDSl(elasticsearch_client)

    zoom_obs = parser_blob_to_es_docs(data)
    index_name = "zoom_index"

    for zoom_doc in zoom_obs:
        assert zoom_doc
        dsl.insert_document(document=zoom_doc)
    search_response: Iterable = dsl.search(index_name)

    for response in search_response:
        assert response
