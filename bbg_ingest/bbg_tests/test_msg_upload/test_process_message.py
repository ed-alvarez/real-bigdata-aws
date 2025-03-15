from pathlib import Path

import pytest
from bbg_helpers.es_bbg_msg_index import BBG_MSG, bloomberg_id
from bbg_helpers.helper_fingerprint import FingerprintHelper
from bbg_src.msg_upload_lambda.parse_msg_xml_file import ProcessMessage
from bbg_tests.fixtures.bbg_msg import (
    msg_bodies,
    msg_recipient_xml_str,
    msg_user_xml_str,
)
from lxml import etree as ET

BASE_DIR = Path(__file__).resolve().parent.parent

message_XML_no_attach = ET.parse(f"{BASE_DIR}/fixtures/bbg_msg/single_message_no_attach.msg.200316.xml")
message_XML_no_attach_root = message_XML_no_attach.getroot()

tarFileName = f"/{BASE_DIR}/fixtures/2020-03-16/decoded/f848135.att.200316.tar.gz"
tar_file_contents = open(tarFileName, "rb").read()


@pytest.fixture
def process_message_obj(emailXML=message_XML_no_attach_root):
    message_obj: ProcessMessage = ProcessMessage(
        emailXML=emailXML,
        fingerprintMeta=FingerprintHelper(),
        Attachments_FileName=tarFileName,
        Attachments_FileContent=tar_file_contents,
    )
    yield message_obj


class TestIgnoreAttachment:
    testAttachment_1_XML: ET = ET.fromstring("<Attachment><Reference>RUNZ READONLY 5E6BDF4600022A712929B39A</Reference></Attachment>")
    testAttachment_2_XML: ET = ET.fromstring(
        "<Attachment><FileName>20200314.Mkt_Cap_EUR50M_DevEur.csv</FileName><FileID>5E6C4FF600007A3007F534C6.csv</FileID><FileSize>4037</FileSize></Attachment>"
    )

    CASES = [(testAttachment_1_XML, False), (testAttachment_2_XML, True)]

    @pytest.mark.parametrize("input, expected", CASES)
    def test_ignore_attachment(self, input, expected, process_message_obj):
        response: bool = process_message_obj._ignore_attachment(attachmentXML=input)
        assert response is expected


class TestCleanSubject:
    CASES = [
        ("GS: NOVARTIS (NOVNVX) CASH                                     ¤", "GS: NOVARTIS (NOVNVX) CASH"),
        (
            "SEAPORT DISTRESSED: FRONTIER COMMUNICATIONS UPDATE",
            "SEAPORT DISTRESSED: FRONTIER COMMUNICATIONS UPDATE",
        ),
        (
            "GSEM: 5Y  RUSSIA  227½/247½  +27½                              ¤",
            "GSEM: 5Y RUSSIA 227½/247½ +27½",
        ),
    ]

    @pytest.mark.parametrize("input, expected", CASES)
    def test_clean_subject(self, input, expected, process_message_obj):
        response: str = process_message_obj._clean_subject(subject_text=input)
        assert response == expected


class TestCleanBody:
    def test_clean_body(self, process_message_obj):
        response: str = process_message_obj._clean_body(body_text=msg_bodies.body_4)
        assert ".bbScopedStyle2606250418267566" not in response


class TestParseUser:
    def test_parse_user(self, process_message_obj):

        user_xml: ET = ET.fromstring(msg_user_xml_str.user_3)
        response: bloomberg_id = process_message_obj._parse_user(userXML=user_xml)
        assert response.bloombergemailaddress == "JZHAO195@Bloomberg.net"
        assert "corporateemailaddress" not in response


class TestProcessESBBGUserl:
    CASES = [
        (msg_recipient_xml_str.user_1, "bloomberg.net"),
        (msg_recipient_xml_str.user_2, "system2capital.com"),
        (msg_recipient_xml_str.user_3, "system2capital.com"),
        (msg_recipient_xml_str.user_4, "bloomberg.net"),
        (msg_recipient_xml_str.user_5, "bloomberg.net"),
    ]

    @pytest.mark.parametrize("input, expected", CASES)
    def test_process_es_bbg_user(self, input, expected, process_message_obj):
        user_xml: ET = ET.fromstring(input)
        response: bloomberg_id = process_message_obj._process_es_bbg_user(bbguserXML=user_xml)
        assert response.domain == expected


class TestProcessEmail:

    message_XML_csv = ET.parse(f"{BASE_DIR}/fixtures/bbg_msg/single_message_csv_attach.msg.200316.xml")
    message_XML_pdf = ET.parse(f"{BASE_DIR}/fixtures/bbg_msg/single_message_pdf_attach.msg.200316.xml")
    message_XML_two_jpg = ET.parse(f"{BASE_DIR}/fixtures/bbg_msg/single_message_two_jpg.msg.200316.xml")

    CASES = [
        (message_XML_no_attach, "5E6F710E00017BD52924067D"),
        (message_XML_csv, "5E6C4A110000928B04860213"),
        (message_XML_pdf, "5E6F710C012601D600870105"),
        (message_XML_two_jpg, "5E6FB93C0120077E01D80231"),
    ]

    @pytest.mark.parametrize("input, expected", CASES)
    def test_process_email(self, input, expected):
        email_xml = input.getroot()
        message_obj: ProcessMessage = ProcessMessage(
            emailXML=email_xml,
            fingerprintMeta=FingerprintHelper(),
            Attachments_FileName=tarFileName,
            Attachments_FileContent=tar_file_contents,
        )

        response: BBG_MSG = message_obj.process_email()
        assert response.es_id == expected
