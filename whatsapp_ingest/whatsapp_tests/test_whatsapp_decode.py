from typing import List, Tuple

import pytest

from whatsapp_ingest.whatsapp_helpers.es_whatsapp_index import (
    Fingerprint_Meta,
    Sentiment,
    SubjectDetail,
    Whatsapp_Id,
)
from whatsapp_ingest.whatsapp_src.whatsapp_decode import whatsappParser


@pytest.fixture()
def whatsapp_parser() -> whatsappParser:
    yield whatsappParser(email_body="", fingerprint_meta=Fingerprint_Meta())


class TestPopulateSubject:
    subject_1: str = "A test subject"
    result_1: SubjectDetail = SubjectDetail()
    result_1.has_subject = True
    result_1.subject_sentiment = Sentiment()
    result_1.subject_sentiment.neu = 1.0

    subject_2: str = ""
    result_2: SubjectDetail = SubjectDetail()
    result_2.has_subject = False
    result_2.subject_sentiment = Sentiment()
    result_2.subject_sentiment.neu = None

    CASES = [(subject_1, result_1), (subject_2, result_2)]

    @pytest.mark.parametrize("input,expected", CASES)
    def test_populate_subject_detail(self, whatsapp_parser, input, expected):
        result: SubjectDetail() = whatsapp_parser._populate_subject_detail(es_subject=input)
        assert result.has_subject == expected.has_subject
        assert result.subject_sentiment.neu == expected.subject_sentiment.neu


class TestToDetailField:
    address_part_1: List[Tuple[str, str]] = [("447786910895", "james@ip-sentinel.com")]
    whatsapp_id_1: Whatsapp_Id = Whatsapp_Id()
    whatsapp_id_1.whatsapp_id = "447786910895"
    whatsapp_id_1.domain = "ip-sentinel.com"
    whatsapp_id_1.corporateemailaddress = "james@ip-sentinel.com"
    result_1: List[Whatsapp_Id] = [whatsapp_id_1]

    CASES = [(address_part_1, result_1)]

    @pytest.mark.parametrize("input,expected", CASES)
    def test_to_detail(self, whatsapp_parser, input, expected):
        result: List[Whatsapp_Id] = whatsapp_parser._generate_whatsapp_id_from_email_addr(address_part=input)
        assert result == expected


class TestToField:
    address_part_1: List[Tuple[str, str]] = [
        ("447786910895", "james@ip-sentinel.com"),
        ("447786919999", "fred@basset.com"),
    ]
    result_1: List[str] = ["james@ip-sentinel.com", "fred@basset.com"]

    CASES = [(address_part_1, result_1)]

    @pytest.mark.parametrize("input,expected", CASES)
    def test_basic_to(self, whatsapp_parser, input, expected):
        result: List[str] = whatsapp_parser._generate_es_to_from_email_addr(address_part=input)
        assert result == expected
