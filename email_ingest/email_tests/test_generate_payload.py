from pathlib import Path

import pytest
from email_src.email_utils.email_payload import EmailPayload
from email_src.email_utils.generate_email_obj import parseMIME

BASE_DIR = Path(__file__).resolve().parent.parent


def mime_file(file_id):
    mime_file_to_open = open(f"{BASE_DIR}/email_tests/sample_emails/" + str(file_id), "rb")
    msg = mime_file_to_open.read()
    return msg


def email_object(file_id):
    email = parseMIME()
    email.byteMail = mime_file(file_id=file_id)
    email.process_message()
    return email


class TestGeneratePayload:
    def test_simple_MIME(self):
        mime_file_id = "sample_MIME"
        payload = EmailPayload()
        payload.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        payload.populate_payload()
        assert "Please verify your new login email." in payload.emailPayload.body
        assert "Please verify your new login email" in payload.emailPayload.subject

    def test_encoded_MIME(self):
        mime_file_id = "b64encodedmime"
        payload = EmailPayload()
        payload.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        payload.populate_payload()
        assert "Ok, thank you." in payload.emailPayload.body
        assert "RE: Meraj  - Monthly Meeting - North Rock Managers" in payload.emailPayload.subject
        assert payload.emailPayload.body_detail.body_sentiment.compound == pytest.approx(0.8074)
        assert payload.emailPayload.body_detail.body_sentiment.neg == pytest.approx(0.0)
        assert payload.emailPayload.body_detail.body_sentiment.neu == pytest.approx(0.325)
        assert payload.emailPayload.body_detail.body_sentiment.pos == pytest.approx(0.675)
        assert "Antoine is back tomorrow so I will move it to Fri." in payload.emailPayload.body_detail.full_body

    def test_badly_formatted_meeting_and_extended_char_in_body(self):
        mime_file_id = "valeur_calendar"
        payload = EmailPayload()
        payload.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        payload.populate_payload()
        assert "Qualità dell’aria interna" in payload.emailPayload.body
        assert "Il tuo webinar: Qualità dell’aria interna: dalla filtrazione alla sanificazione" in payload.emailPayload.subject

    def test_complex_meeting(self):
        mime_file_id = "complex_meeting"
        payload = EmailPayload()
        payload.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        payload.populate_payload()
        assert "location : Rac Club Pall Mall" in payload.emailPayload.body
        assert "Fingerprint Test Meeting 2" in payload.emailPayload.subject

    def test_single_word_body(self):
        mime_file_id = "single_word_body"
        payload = EmailPayload()
        payload.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        payload.populate_payload()
        assert "Test" in payload.emailPayload.body

    def test_missing_body_due_to_external_email_warning(self):
        mime_file_id = "owl_rock_body_missing"
        payload = EmailPayload()
        payload.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        payload.populate_payload()
        assert "Sorry for not coming back to you" in payload.emailPayload.body

    def test_encoded_fields(self):
        mime_file_id = "think-thread-decode"
        payload = EmailPayload()
        payload.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        payload.populate_payload()
        assert "Management roadshow starts tonight" in payload.emailPayload.body
        assert payload.emailPayload.subject == "**HSBC Deal: Sirnaomics Ltd. HK IPO ¨C LAUNCH ** Approved external email"

    def test_missing_to(self):
        mime_file_id = "melqart_error_1"
        payload = EmailPayload()
        payload.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        payload.populate_payload()
        assert "This message was originally sent to CAN OZDEMIR via the Bloomberg Terminal." in payload.emailPayload.body
        assert payload.emailPayload.subject == "Известия: Disney назвал дату премьеры мини-сериала Marvel «ВандаВижен»"

    def test_think_timeout(self):
        mime_file_id = "think_timeout"
        payload = EmailPayload()
        payload.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        payload.populate_payload()
        assert "Flops and bad advisors" in payload.emailPayload.body
