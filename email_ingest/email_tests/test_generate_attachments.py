import os
from pathlib import Path

import pytest
from elasticsearch_dsl import AttrList
from email_src.email_utils.generate_email_obj import parseMIME
from email_src.email_utils.individual_email_process import EmailAttachments

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


class TestGenerateAttachmemnts:
    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_meeting_attachment(self):
        mime_file_id = "complex_meeting"
        attachments = EmailAttachments()
        attachments.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        attachments.populate_attachments()
        assert "Information Security Policy" in attachments.emailAttachments.attachments[0].content
        assert attachments.emailAttachments.attachments[0].attachment_size == pytest.approx(17934, rel=5)
        assert attachments.emailAttachments.attachments[0].filename == "Information Security Policy.docx"
        assert attachments.emailAttachments.attachments_detail.has_attachment == True

    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_no_attachment(self):
        mime_file_id = "sample_MIME"
        attachments = EmailAttachments()
        attachments.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        attachments.populate_attachments()
        assert attachments.emailAttachments.attachments_detail.has_attachment == False
        assert type(attachments.emailAttachments.attachments) is AttrList

    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_pdf_attachment(self):
        mime_file_id = "tangency_pdf_fail"
        attachments = EmailAttachments()
        attachments.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        attachments.populate_attachments()
        assert "We think that the renminbi’s appreciation has further to run" in attachments.emailAttachments.attachments[0].content
        assert attachments.emailAttachments.attachments[0].attachment_size == pytest.approx(12391, rel=5)
        assert (
            attachments.emailAttachments.attachments[0].filename
            == "Capital Daily - We think that the renminbis appreciation has further to run.pdf"
        )
        assert attachments.emailAttachments.attachments_detail.has_attachment == True

    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_zero_parsable_content(self):
        mime_file_id = "mirabella_attachment_01"
        attachments = EmailAttachments()
        attachments.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        attachments.populate_attachments()
        assert "" in attachments.emailAttachments.attachments[0].content
        assert "attachment_size" not in attachments.emailAttachments.attachments[0]
        assert attachments.emailAttachments.attachments[0].filename == "Iconic buildings.docx"
        assert attachments.emailAttachments.attachments_detail.has_attachment == True

    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_attachment_and_token(self):
        mime_file_id = "valeur_multiple_attachments"
        attachments = EmailAttachments()
        attachments.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        attachments.populate_attachments()
        assert "We hope this letter finds you and yours in good spirits" in attachments.emailAttachments.attachments[0].content
        assert attachments.emailAttachments.attachments[0].attachment_size == pytest.approx(54035, rel=5)
        assert (
            attachments.emailAttachments.attachments[0].filename
            == "Q3 2020 Quarterly Letter - Stable Seed Fund 2018 - Prepared for Valeur.pdf"
        )

        assert "" in attachments.emailAttachments.attachments[1].content
        assert "attachment_size" not in attachments.emailAttachments.attachments[1]
        assert attachments.emailAttachments.attachments[1].filename == "ATPFile_CE6EEE48-3663-4393-AEBB-9A55F7C1723F.token"
        assert attachments.emailAttachments.attachments_detail.has_attachment == True

    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_multiple_attachments(self):
        mime_file_id = "system2_with_attachments_2"
        attachments = EmailAttachments()
        attachments.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        attachments.populate_attachments()
        assert "MSCI China Semi-Annual Index Review Nov 2020" in attachments.emailAttachments.attachments[0].content
        assert attachments.emailAttachments.attachments[0].attachment_size == pytest.approx(144785, rel=5)
        assert attachments.emailAttachments.attachments[0].filename == "MSCI_CH,HK_Nov2020_20201111.xlsm"

        assert "MSCI Singapore Semi-Annual Index Review Nov 2020" in attachments.emailAttachments.attachments[1].content
        assert attachments.emailAttachments.attachments[1].attachment_size == pytest.approx(33626, rel=5)
        assert attachments.emailAttachments.attachments[1].filename == "MSCI_ASEAN_Nov2020_20201111.xlsm"

        assert "MSCI Japan Semi-Annual Index Review Nov 2020" in attachments.emailAttachments.attachments[2].content
        assert attachments.emailAttachments.attachments[2].attachment_size == pytest.approx(77647, rel=5)
        assert attachments.emailAttachments.attachments[2].filename == "MSCI_Japan_Nov2020_20201111.xlsm"

        assert "MSCI EM Asia Semi-Annual Index Review Nov 2020" in attachments.emailAttachments.attachments[3].content
        assert attachments.emailAttachments.attachments[3].attachment_size == pytest.approx(205844, rel=5)
        assert attachments.emailAttachments.attachments[3].filename == "MSCI_EM_Asia_Nov2020_20201111.xlsm"

        assert "MSCI DM Asia Semi-Annual Index Review Nov 2020" in attachments.emailAttachments.attachments[4].content
        assert attachments.emailAttachments.attachments[4].attachment_size == pytest.approx(108246, rel=5)
        assert attachments.emailAttachments.attachments[4].filename == "MSCI_DM_Asia_Nov2020_20201111.xlsm"

        assert attachments.emailAttachments.attachments_detail.has_attachment == True

    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_multiple_attachments_encrypted_csv(self):
        mime_file_id = "kirkoswold_attachment_01"
        attachments = EmailAttachments()
        attachments.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        attachments.populate_attachments()
        assert "DD7888CC2F089845C3417B208A4E9701" in attachments.emailAttachments.attachments[0].content
        assert attachments.emailAttachments.attachments[0].attachment_size == pytest.approx(1854, rel=5)
        assert attachments.emailAttachments.attachments[0].filename == "OTC-MitsubishiforKirkoswald-OTC204X.20201112.csv"

        assert "KIRKOSWALD CAPITAL PARTNERS" in attachments.emailAttachments.attachments[1].content
        assert attachments.emailAttachments.attachments[1].attachment_size == pytest.approx(56002, rel=5)
        assert attachments.emailAttachments.attachments[1].filename == "Kirkoswald-LNCentral-MAC001X.20201112.2321.csv"

        assert "" in attachments.emailAttachments.attachments[2].content
        assert "attachment_size" not in attachments.emailAttachments.attachments[2]
        assert attachments.emailAttachments.attachments[2].filename == "LN-CentralSwapExtracts.131120.0055.zip.pgp.csv"
        assert attachments.emailAttachments.attachments[2].error == "No processing for the zip file type is implimented yet"
        assert attachments.emailAttachments.attachments_detail.has_attachment == True

    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_attachments_filename_in_content_disposition(self):
        mime_file_id = "hanetf_no_file_in_type"
        attachments = EmailAttachments()
        attachments.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        attachments.populate_attachments()
        assert "Corporate Actions Forecast" in attachments.emailAttachments.attachments[0].content
        assert attachments.emailAttachments.attachments[0].attachment_size == pytest.approx(4494, rel=5)
        assert attachments.emailAttachments.attachments[0].filename == "MEDCAWEP_DCAF_2020-11-16.csv"
        assert attachments.emailAttachments.attachments_detail.has_attachment == True

    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_attachments_filename_in_content_type(self):
        mime_file_id = "kirkoswold_no_application_error"
        attachments = EmailAttachments()
        attachments.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        attachments.populate_attachments()
        assert "" in attachments.emailAttachments.attachments[0].content
        assert "attachment_size" not in attachments.emailAttachments.attachments[0]
        assert attachments.emailAttachments.attachments[0].filename == "application-pdf.png"
        assert attachments.emailAttachments.attachments[0].error == "No processing for the png file type is implimented yet"
        assert attachments.emailAttachments.attachments_detail.has_attachment == True

        assert "Energy Midday Quicksheet" in attachments.emailAttachments.attachments[1].content
        assert attachments.emailAttachments.attachments[1].attachment_size == pytest.approx(1258, rel=5)
        assert attachments.emailAttachments.attachments[1].filename == "noonenergyquicksheeteuroop1116.pdf"

    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_attachments_filename_with_separator_char(self):
        mime_file_id = "rbh_index_out_range"
        attachments = EmailAttachments()
        attachments.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        attachments.populate_attachments()
        assert "MRW has made the most headway on price cuts in 2H20" in attachments.emailAttachments.attachments[0].content
        assert attachments.emailAttachments.attachments[0].attachment_size == pytest.approx(92478, rel=5)
        assert (
            attachments.emailAttachments.attachments[0].filename
            == "Morrison (Wm) (MRW.L)_ Online moves to tailwind from headwind, driving further LFL outperformance; upgrade to Buy from Sell.pdf"
        )
        assert attachments.emailAttachments.attachments_detail.has_attachment == True
