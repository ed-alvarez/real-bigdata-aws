import datetime
import os
from email.message import EmailMessage
from pathlib import Path

import pytest
from email_helpers.es_email_index_v2 import Attachment, Email_Id
from email_helpers.helper_fingerprint import FingerprintHelper
from email_src.email_utils.individual_email_process import EMAILObject

BASE_DIR = Path(__file__).resolve().parent.parent

test_email_message = EmailMessage()

fingerprint_metadata = FingerprintHelper()
fingerprint_metadata.clientName = "test"
fingerprint_metadata.key_name = "123456789"
fingerprint_metadata.bucket_name = "test.ips"
fingerprint_metadata.msg_type = "email"
fingerprint_metadata.processedTime = None


def mime_file(file_id):
    mime_file_to_open = open(f"{BASE_DIR}/email_tests/sample_emails/" + str(file_id), "rb")
    msg = mime_file_to_open.read()
    return msg


class TestEmailObject:
    def test_simple_MIME_email(self):
        mime_file_id = "sample_MIME"
        email_date = datetime.datetime(2018, 4, 28, 11, 10, 17)
        email = EMAILObject()
        email.byteMail = mime_file(file_id=mime_file_id)
        email.process_message()

        to_address = Email_Id()
        to_address = email.email.to_detail[0]
        assert to_address["corporateemailaddress"] == "james@ip-sentinel.com"
        assert to_address["firstname"] == ""
        assert to_address["lastname"] == "james"
        assert to_address["domain"] == "ip-sentinel.com"

        from_address = Email_Id()
        from_address = email.email.from_detail
        assert from_address["corporateemailaddress"] == "noreply@siteground.com"
        assert from_address["firstname"] == "Site"
        assert from_address["lastname"] == "Ground"
        assert from_address["domain"] == "siteground.com"

        assert not email.email.cc
        assert email.email.subject == "Please verify your new login email"
        assert "Please verify your new login email" in email.email.body
        assert not email.email.attachments
        assert email.email.message_id == "e78bda08dbec3e5fab8a786cc10a37839bb23c43@siteground.com"
        assert email.email.date == email_date
        assert email.email.message_id_detail.has_thread is False
        assert not email.email.message_id_detail.thread_index
        assert email.email.body_detail.body_sentiment.compound == pytest.approx(0.8271)
        assert email.email.body_detail.body_sentiment.neg == pytest.approx(0.035)
        assert email.email.body_detail.body_sentiment.neu == pytest.approx(0.8, 0.1)
        assert email.email.body_detail.body_sentiment.pos == pytest.approx(0.164, 0.1)

    def test_simple_MIME_HTML_only_email(self):
        mime_file_id = "sample_MIME_HTML_only"
        email_date = datetime.datetime(2018, 4, 28, 11, 10, 17)
        email = EMAILObject()
        email.byteMail = mime_file(file_id=mime_file_id)
        email.process_message()

        to_address = Email_Id()
        to_address = email.email.to_detail[0]
        assert to_address["corporateemailaddress"] == "james@ip-sentinel.com"
        assert to_address["firstname"] == ""
        assert to_address["lastname"] == "james"
        assert to_address["domain"] == "ip-sentinel.com"

        from_address = Email_Id()
        from_address = email.email.from_detail
        assert from_address["corporateemailaddress"] == "noreply@siteground.com"
        assert from_address["firstname"] == "Site"
        assert from_address["lastname"] == "Ground"
        assert from_address["domain"] == "siteground.com"

        assert not email.email.cc
        assert email.email.subject == "Please verify your new login email"
        assert "Please verify your new login email" in email.email.body
        assert "/* <![CDATA[ */" not in email.email.body  # Check no HTM in plain body
        assert not email.email.attachments
        assert email.email.message_id == "e78bda08dbec3e5fab8a786cc10a37839bb23c43@siteground.com"
        assert email.email.date == email_date
        assert email.email.message_id_detail.has_thread is False
        assert not email.email.message_id_detail.thread_index
        assert email.email.body_detail.body_sentiment.compound == pytest.approx(0.5423)
        assert email.email.body_detail.body_sentiment.neg == pytest.approx(0.04)
        assert email.email.body_detail.body_sentiment.neu == pytest.approx(0.8, 0.1)
        assert email.email.body_detail.body_sentiment.pos == pytest.approx(0.116, 0.1)

    def test_simple_MIME_plain_only_email(self):
        mime_file_id = "sample_MIME_plain_only"
        email_date = datetime.datetime(2018, 4, 28, 11, 10, 17)
        email = EMAILObject()
        email.byteMail = mime_file(file_id=mime_file_id)
        email.process_message()

        to_address = Email_Id()
        to_address = email.email.to_detail[0]
        assert to_address["corporateemailaddress"] == "james@ip-sentinel.com"
        assert to_address["firstname"] == ""
        assert to_address["lastname"] == "james"
        assert to_address["domain"] == "ip-sentinel.com"

        from_address = Email_Id()
        from_address = email.email.from_detail
        assert from_address["corporateemailaddress"] == "noreply@siteground.com"
        assert from_address["firstname"] == "Site"
        assert from_address["lastname"] == "Ground"
        assert from_address["domain"] == "siteground.com"

        assert not email.email.cc
        assert email.email.subject == "Please verify your new login email"
        assert "Please verify your new login email" in email.email.body
        assert not email.email.attachments
        assert email.email.attachments_detail.has_attachment == False
        assert email.email.message_id == "e78bda08dbec3e5fab8a786cc10a37839bb23c43@siteground.com"
        assert email.email.date == email_date
        assert email.email.message_id_detail.has_thread is False
        assert not email.email.message_id_detail.thread_index
        assert email.email.body_detail.body_sentiment.compound == pytest.approx(0.8271)
        assert email.email.body_detail.body_sentiment.neg == pytest.approx(0.035)
        assert email.email.body_detail.body_sentiment.neu == pytest.approx(0.8, 0.1)
        assert email.email.body_detail.body_sentiment.pos == pytest.approx(0.164, 0.1)

    def test_encoded_MIME_email(self):
        mime_file_id = "b64encodedmime"
        email_date = datetime.datetime(2019, 6, 6, 14, 43, 25)
        email = EMAILObject()
        email.byteMail = mime_file(file_id=mime_file_id)
        email.process_message()

        from_address = Email_Id()
        from_address = email.email.to_detail[0]
        assert from_address["corporateemailaddress"] == "meraj@bradburycap.com"
        assert from_address["firstname"] == "Meraj"
        assert from_address["lastname"] == "Sepehrnia"
        assert from_address["domain"] == "bradburycap.com"

        to_address = Email_Id()
        to_address = email.email.from_detail
        assert to_address["corporateemailaddress"] == "angelika.paszek@lighthousepartners.com"
        assert to_address["firstname"] == "Angelika"
        assert to_address["lastname"] == "Paszek"
        assert to_address["domain"] == "lighthousepartners.com"

        assert not email.email.cc
        assert email.email.subject == "RE: Meraj  - Monthly Meeting - North Rock Managers"
        assert "Ok, thank you." in email.email.body
        assert not email.email.attachments
        assert email.email.attachments_detail.has_attachment == False
        assert email.email.message_id == "<DM5PR17MB11643D009805A8B9BA5B690D88170@DM5PR17MB1164.namprd17.prod.outlook.com>"
        assert email.email.date == email_date
        assert email.email.message_id_detail.has_thread is True
        assert (
            email.email.message_id_detail.thread_index
            == "AdUbhvU9xsWueWIhQ4mjjss/H7SnNgAABT1wAAJULJgAAHytIAA4by6gAAAMiHAAAGt5QAAADhng"
        )
        assert email.email.message_id_detail.thread_topic == "Meraj  - Monthly Meeting - North Rock Managers"
        assert email.email.body_detail.body_sentiment.compound == pytest.approx(0.8074)
        assert email.email.body_detail.body_sentiment.neg == pytest.approx(0.0)
        assert email.email.body_detail.body_sentiment.neu == pytest.approx(0.325, 0.1)
        assert email.email.body_detail.body_sentiment.pos == pytest.approx(0.675, 0.1)

    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_complex_meeting(self):
        mime_file_id = "complex_meeting"
        email_date = datetime.datetime(2019, 8, 9, 15, 15, 30)
        email = EMAILObject()
        email.byteMail = mime_file(file_id=mime_file_id)
        email.process_message()

        to_address = Email_Id()
        to_address = email.email.to_detail[0]
        assert to_address["corporateemailaddress"] == "james@hogbin.com"
        assert to_address["firstname"] == "James"
        assert to_address["lastname"] == "Hogbin"
        assert to_address["domain"] == "hogbin.com"

        from_address = Email_Id()
        from_address = email.email.from_detail
        assert from_address["corporateemailaddress"] == "james@ip-sentinel.com"
        assert from_address["firstname"] == "James"
        assert from_address["lastname"] == "Hogbin"
        assert from_address["domain"] == "ip-sentinel.com"

        cc_address = Email_Id()
        cc_address = email.email.cc_detail[0]
        assert cc_address["corporateemailaddress"] == "hogbin@gmail.com"
        assert cc_address["firstname"] == "James"
        assert cc_address["lastname"] == "Hogbin"
        assert cc_address["domain"] == "gmail.com"

        assert email.email.subject == "Fingerprint Test Meeting 2"
        assert "organiser : james@ip-sentinel.com" in email.email.body
        assert email.email.attachments_detail.has_attachment == True

        assert email.email.message_id == "<DB8PR10MB33857BD818BA3ADC085C433BF3D60@DB8PR10MB3385.EURPRD10.PROD.OUTLOOK.COM>"
        assert email.email.date == email_date
        assert email.email.message_id_detail.has_thread is True
        assert email.email.message_id_detail.thread_index == "AdVOxPcTT6bp4Qlf50SYnv6fWang+Q=="
        assert email.email.message_id_detail.thread_topic == "Fingerprint Test Meeting 2"
        assert email.email.body_detail.body_sentiment.compound == pytest.approx(0.516)
        assert email.email.body_detail.body_sentiment.neg == pytest.approx(0.0)
        assert email.email.body_detail.body_sentiment.neu == pytest.approx(0.926, 0.1)
        assert email.email.body_detail.body_sentiment.pos == pytest.approx(0.058)

        attachment = Attachment()
        attachment = email.email.attachments[0]
        assert "Information Security Policy.docx" in attachment.filename
        assert "Information Security Policy\nPurpose\nThis" in attachment.content
        assert attachment.attachment_size == pytest.approx(17934, rel=5)

    def test_single_word_body(self):
        mime_file_id = "single_word_body"
        email = EMAILObject()
        email.byteMail = mime_file(file_id=mime_file_id)
        email.process_message()

        assert "Test" in email.email.body

    def test_broken_html_1(self):
        mime_file_id = "broken_html_1"
        email = EMAILObject()
        email.byteMail = mime_file(file_id=mime_file_id)
        email.process_message()
        assert "Task Exit alerts are generated when a task execution completes" in email.email.body
