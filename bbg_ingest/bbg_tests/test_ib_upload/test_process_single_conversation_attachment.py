import os
from pathlib import Path

import pytest
from bbg_helpers.es_bbg_ib_index import BBG_IB
from bbg_helpers.es_bbg_ib_index import attachment as es_attachment
from bbg_helpers.es_bbg_ib_index import bloomberg_id
from bbg_src.ib_upload_lambda.bbg_ib_conversation.process_single_conversation import (
    msgToGroup,
)
from bbg_src.ib_upload_lambda.bbg_ib_conversation.process_single_conversation_attachment import (
    ProcessSingleAttachment,
)
from lxml import etree as ET

user_0 = bloomberg_id()
user_0.loginname = "BJNIXON"
user_0.firstname = "BEN"
user_0.lastname = "NIXON"
user_0.companyname = "JEFFERIES INTERNATIO"
user_0.emailaddress = "BJNIXON@Bloomberg.net"
user_0.domain = "bloomberg.net"

user_1 = bloomberg_id()
user_1.loginname = "LUDOCOHEN"
user_1.firstname = "LUDOVIC"
user_1.lastname = "COHEN"
user_1.companyname = "JEFFERIES INTERNATIO"
user_1.emailaddress = "LUDOCOHEN@Bloomberg.net"
user_1.domain = "bloomberg.net"

user_2 = bloomberg_id()
user_2.loginname = "SEANSYSTEM2"
user_2.firstname = "SEAN"
user_2.lastname = "OLDFIELD"
user_2.uuid = "25813826"
user_2.firmnumber = "848135"
user_2.accountnumber = "30413594"
user_2.companyname = "MIRABELLA FINANCIAL"
user_2.emailaddress = "SEANSYSTEM2@Bloomberg.net"
user_2.corporateemailaddress = "sean@system2capital.com"
user_2.domain = "system2capital.com"

BASE_DIR = Path(__file__).resolve().parent.parent
tarFileName = f"{BASE_DIR}/fixtures/2020-03-16/decoded/f848135.att.200316.tar.gz"
tar_file_contents = open(tarFileName, "rb").read()

messagexml_gif_file = ET.fromstring(
    """<Attachment InteractionType="NH">
                                    <User>
                                    <LoginName>SEANSYSTEM2</LoginName>
                                    <FirstName>SEAN</FirstName>
                                    <LastName>OLDFIELD</LastName>
                                    <UUID>25813826</UUID>
                                    <FirmNumber>848135</FirmNumber>
                                    <AccountNumber>30413594</AccountNumber>
                                    <CompanyName>MIRABELLA FINANCIAL</CompanyName>
                                    <EmailAddress>SEANSYSTEM2@Bloomberg.net</EmailAddress>
                                    <CorporateEmailAddress>sean@system2capital.com</CorporateEmailAddress>
                                    </User>
                                    <DateTime>03/16/2020 16:37:21</DateTime>
                                    <DateTimeUTC>1584376641</DateTimeUTC>
                                    <ConversationID>PCHAT-0x10000027FD8A5</ConversationID>
                                    <FileName>BloombergGRIB_2020031659826.gif</FileName>
                                    <FileID>5E6FAB380000F0D307F41FE3.gif</FileID>
                                    <FileSize>48721</FileSize>
                                    </Attachment>"""
)

bbg_attachment_gif: es_attachment = es_attachment()
bbg_attachment_gif.fileid = "5E6FAB380000F0D307F41FE3.gif"
bbg_attachment_gif.filename = "BloombergGRIB_2020031659826.gif"
bbg_attachment_gif.filesize = "48721"

messagexml_pdf_file = ET.fromstring(
    """<Attachment InteractionType="NH">
                                   <User>
                                   <LoginName>CCHANCHORLE1</LoginName>
                                   <FirstName>CHRISTOPHE</FirstName>
                                   <LastName>CHANCHORLE</LastName>
                                   <CompanyName>STIFEL NICOLAUS EURO</CompanyName>
                                   <EmailAddress>CCHANCHORLE1@Bloomberg.net</EmailAddress>
                                   <CorporateEmailAddress></CorporateEmailAddress>
                                   </User>
                                   <DateTime>03/16/2020 16:06:24</DateTime>
                                   <DateTimeUTC>1584374784</DateTimeUTC>
                                   <ConversationID>PCHAT-0x100000281F08A</ConversationID>
                                   <FileName>Travel &amp; Transport grounded  Thinking about liquidity.pdf</FileName>
                                   <FileID>5E6FA3FF0000F0D307F41E72.pdf</FileID>
                                   <FileSize>904414</FileSize>
                                   </Attachment>"""
)

bbg_attachment_pdf: es_attachment = es_attachment()
bbg_attachment_pdf.fileid = "5E6FA3FF0000F0D307F41E72.pdf"
bbg_attachment_pdf.filename = "Travel & Transport grounded  Thinking about liquidity.pdf"
bbg_attachment_pdf.filesize = "904414"


class TestFunctions:
    def test_basic_decode_with_from(self):
        user_list = msgToGroup()
        process_message_obj = ProcessSingleAttachment(
            attachmentXML=messagexml_gif_file,
            attachmentUsers=user_list,
            Attachments_FileName=tarFileName,
            Attachments_FileContent=tar_file_contents,
        )
        response_BBG_IB, response_BBG_Attachment_Item = process_message_obj._create_es_BBG_IB_from_XML(
            attachmentXML=messagexml_gif_file, messageUsers=user_list
        )
        assert isinstance(response_BBG_IB, BBG_IB)
        assert response_BBG_IB.from_detail == user_2
        assert response_BBG_IB.conversationid == "PCHAT-0x10000027FD8A5"
        assert response_BBG_Attachment_Item.fileid == "5E6FAB380000F0D307F41FE3.gif"
        assert response_BBG_Attachment_Item.filename == "BloombergGRIB_2020031659826.gif"
        assert response_BBG_Attachment_Item.filesize == "48721"

    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_get_content_pdf(self):
        user_list = msgToGroup()
        process_message_obj = ProcessSingleAttachment(
            attachmentXML=messagexml_pdf_file,
            attachmentUsers=user_list,
            Attachments_FileName=tarFileName,
            Attachments_FileContent=tar_file_contents,
        )
        response: es_attachment = process_message_obj._get_content(es_attachment_detail=bbg_attachment_pdf)
        assert "Indicative offer pricing as per Stifel Trading Desk 16 March 2020 mid-day" in response.content

    def test_get_content_file_not_found_in_tar(self):
        user_list = msgToGroup()
        process_message_obj = ProcessSingleAttachment(
            attachmentXML=messagexml_pdf_file,
            attachmentUsers=user_list,
            Attachments_FileName=tarFileName,
            Attachments_FileContent=tar_file_contents,
        )
        # overwrite fileid to force the error
        bbg_attachment_pdf.fileid = "blank"
        response: es_attachment = process_message_obj._get_content(es_attachment_detail=bbg_attachment_pdf)
        assert response.error == f"Attachment {bbg_attachment_pdf.fileid} cannot be extracted from the archive"

    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_get_attachment_detail_graphics_file(self):
        user_list = msgToGroup()
        process_message_obj = ProcessSingleAttachment(
            attachmentXML=messagexml_pdf_file,
            attachmentUsers=user_list,
            Attachments_FileName=tarFileName,
            Attachments_FileContent=tar_file_contents,
        )
        response: es_attachment = process_message_obj._get_attachment_detail(attachment_details=bbg_attachment_gif)
        assert response.error == f"Attachment {bbg_attachment_gif.fileid} is an IMAGE and therefore NOT processed"
        assert response.tar_file_location == "dev.processed.bbg/2020-03-16/decoded/f848135.att.200316.tar.gz"

    def test_full_decode_with_correct_to_address_content(self):
        user_list = msgToGroup()
        user_list.add_user(user_0)
        user_list.add_user(user_1)
        user_list.add_user(user_2)
        process_message_obj = ProcessSingleAttachment(
            attachmentXML=messagexml_pdf_file,
            attachmentUsers=user_list,
            Attachments_FileName=tarFileName,
            Attachments_FileContent=tar_file_contents,
        )
        response: BBG_IB = process_message_obj.process_attachment()
        assert user_0 in response.to_detail
        assert response.from_ == "CHRISTOPHE CHANCHORLE <CCHANCHORLE1@Bloomberg.net>"

    def test_full_decode_with_correct_to_address_no_content(self):
        user_list = msgToGroup()
        user_list.add_user(user_0)
        user_list.add_user(user_1)
        user_list.add_user(user_2)
        process_message_obj = ProcessSingleAttachment(
            attachmentXML=messagexml_gif_file,
            attachmentUsers=user_list,
            Attachments_FileName=tarFileName,
            Attachments_FileContent=tar_file_contents,
        )
        response: BBG_IB = process_message_obj.process_attachment()
        assert user_0 in response.to_detail
        assert user_2 not in response.to_detail
        assert response.from_detail == user_2
