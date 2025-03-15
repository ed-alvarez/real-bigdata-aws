from pathlib import Path

import pytest
from email_src.email_utils.generate_email_obj import parseMIME
from email_src.email_utils.individual_email_process import EmailEnvelope

BASE_DIR = Path(__file__).resolve().parent.parent


def mime_file(file_id):
    mime_file_to_open = open(f"{BASE_DIR}/email_tests/sample_emails/" + str(file_id), "rb")
    msg = mime_file_to_open.read()
    return msg


def email_object(file_id):
    email = parseMIME()
    email.byteMail = mime_file(file_id=file_id)
    email.process_message()
    return email.parsedMIME


class TestGenerateEnvelope:
    def test_simple_MIME(self):
        mime_file_id = "sample_MIME"
        envelope = EmailEnvelope()
        envelope.emailMessage = email_object(file_id=mime_file_id)
        envelope.populate_envelope()
        assert envelope.emailEnvelope.to == "james@ip-sentinel.com"

        to_address = envelope.emailEnvelope.to_detail[0]

        assert to_address["corporateemailaddress"] == "james@ip-sentinel.com"
        assert to_address["firstname"] == ""
        assert to_address["lastname"] == "james"
        assert to_address["domain"] == "ip-sentinel.com"

        from_address = envelope.emailEnvelope.from_detail
        assert from_address["corporateemailaddress"] == "noreply@siteground.com"
        assert from_address["firstname"] == "Site"
        assert from_address["lastname"] == "Ground"
        assert from_address["domain"] == "siteground.com"

        message_detail = envelope.emailEnvelope.message_id_detail
        assert message_detail.has_thread is False

    def test_reply_MIME(self):
        mime_file_id = "b64encodedmime"
        envelope = EmailEnvelope()
        envelope.emailMessage = email_object(file_id=mime_file_id)
        envelope.populate_envelope()

        assert envelope.emailEnvelope.message_id == "<DM5PR17MB11643D009805A8B9BA5B690D88170@DM5PR17MB1164.namprd17.prod.outlook.com>"

        message_detail = envelope.emailEnvelope.message_id_detail
        assert message_detail.has_thread is True
        assert message_detail.thread_index == "AdUbhvU9xsWueWIhQ4mjjss/H7SnNgAABT1wAAJULJgAAHytIAA4by6gAAAMiHAAAGt5QAAADhng"
        assert message_detail.thread_topic == "Meraj  - Monthly Meeting - North Rock Managers"

    def test_chinese_email(self):
        mime_file_id = "investtao_chinese"
        envelope = EmailEnvelope()
        envelope.emailMessage = email_object(file_id=mime_file_id)
        envelope.populate_envelope()
        assert envelope.emailEnvelope.from_ == "魏德星(Alfred Ngai) <alfred.ts.ngai@pingan.com.hk>"

    def test_think_timeout(self):
        mime_file_id = "think_timeout"
        envelope = EmailEnvelope()
        envelope.emailMessage = email_object(file_id=mime_file_id)
        envelope.populate_envelope()
        assert envelope.emailEnvelope.from_ == "screeningalerts@capitaliq.com"


CASES = [
    pytest.param(
        "first_name",
        "Undisclosed recipients:",
        "Contato, Guilherme X <guilherme.x.contato@jpmorgan.com>",
        None,
        id="first_name",
    ),
    pytest.param(
        "aster_japan",
        "conrad.bartos@astercm.com",
        "Robinson, Nicholas  <nicholas.robinson.2@credit-suisse.com>",
        None,
        id="test_jap_code_page",
    ),
    pytest.param(
        "svelland_content_type",
        "tim@svelland.com",
        "Wealth Manager Afternoon <noreply@listserve.citywire.co.uk>",
        None,
        id="test_header_getting_into_translate",
    ),
    pytest.param(
        "system2_with_attachments",
        "Undisclosed recipients:;",
        "Kahn, Lionel <Lionel.Kahn@gs.com>",
        None,
        id="system2_with_attachments",
    ),
]


class TestBulkEmails:
    @pytest.mark.parametrize("file_name, to, from_, cc", CASES)
    def test_bulk_email(self, file_name, to, from_, cc):
        envelope: EmailEnvelope = EmailEnvelope()
        envelope.emailMessage = email_object(file_id=file_name)
        envelope.populate_envelope()
        assert envelope.emailEnvelope.from_ == from_
        assert envelope.emailEnvelope.to == to
        assert envelope.emailEnvelope.cc == cc
