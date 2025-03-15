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
user_0.loginname = "nbradford8"
user_0.firstname = "NICOLAS"
user_0.lastname = "NICOLAS"
user_0.companyname = "KIRKOSWALD CAPITAL PARTNERS LLP"
user_0.emailaddress = "nbradford8@bloomberg.net"
user_0.domain = "kirkoswald.com"

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
tarFileName = f"{BASE_DIR}/fixtures/2021-06-08/decoded/f886973.ib19.att.210608.tar.gz"
tar_file_contents = open(tarFileName, "rb").read()

messagexml_gif_file = ET.fromstring(
    """<Attachment InteractionType="N">
    <User>
      <LoginName>nbradford8</LoginName>
      <FirstName>NICOLAS</FirstName>
      <LastName>BRADFORD</LastName>
      <UUID>29539242</UUID>
      <FirmNumber>886973</FirmNumber>
      <AccountNumber>30357412</AccountNumber>
      <CompanyName>KIRKOSWALD CAPITAL PARTNERS LLP</CompanyName>
      <EmailAddress>nbradford8@bloomberg.net</EmailAddress>
      <CorporateEmailAddress>nick.bradford@kirkoswald.com</CorporateEmailAddress>
    </User>
    <DateTime>06/07/2021 20:40:59</DateTime>
    <DateTimeUTC>1623098459</DateTimeUTC>
    <ConversationID>ADSK-fs:60BE802B4430004A</ConversationID>
    <FileName>screenshot_1623098441593.png</FileName>
    <FileID>29539242_screenshot_1623098441593_60BE845A00C201C806410001.png</FileID>
    <FileSize>10335750</FileSize>
  </Attachment>"""
)

bbg_attachment_gif: es_attachment = es_attachment()
bbg_attachment_gif.fileid = "5E6FAB380000F0D307F41FE3.gif"
bbg_attachment_gif.filename = "BloombergGRIB_2020031659826.gif"
bbg_attachment_gif.filesize = "48721"

messagexml_pdf_file = ET.fromstring(
    """  <Attachment InteractionType="N">
    <User>
      <LoginName>bberber3</LoginName>
      <FirstName>BENITO</FirstName>
      <LastName>BERBER</LastName>
      <CompanyName>NATIXIS NORTH AMERICA LLC</CompanyName>
      <EmailAddress>bberber3@bloomberg.net</EmailAddress>
      <CorporateEmailAddress></CorporateEmailAddress>
    </User>
    <DateTime>06/07/2021 20:20:28</DateTime>
    <DateTimeUTC>1623097228</DateTimeUTC>
    <ConversationID>PCHAT-0x10000027C95CE</ConversationID>
    <FileName>Encuesta_Citibanamex_070621.pdf</FileName>
    <FileID>23933032_encuesta_citibanamex_070621_60BE7F8B00CA00B6064C0001.pdf</FileID>
    <FileSize>365598</FileSize>
  </Attachment>"""
)

bbg_attachment_pdf: es_attachment = es_attachment()
bbg_attachment_pdf.fileid = "23933032_encuesta_citibanamex_070621_60BE7F8B00CA00B6064C0001.pdf"
bbg_attachment_pdf.filename = "Encuesta_Citibanamex_070621.pdf"
bbg_attachment_pdf.filesize = "365598"


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
        assert response_BBG_IB.from_detail.loginname == user_0.loginname
        assert response_BBG_IB.conversationid == "ADSK-fs:60BE802B4430004A"
        assert response_BBG_Attachment_Item.fileid == "29539242_screenshot_1623098441593_60BE845A00C201C806410001.png"
        assert response_BBG_Attachment_Item.filename == "screenshot_1623098441593.png"
        assert response_BBG_Attachment_Item.filesize == "10335750"

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
        assert "Estudios Económicos Encuesta de Expectativas de" in response.content

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
        assert response.tar_file_location == "dev.processed.bbg/2021-06-08/decoded/f886973.ib19.att.210608.tar.gz"

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
        assert response.from_ == "BENITO BERBER <bberber3@bloomberg.net>"

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
        assert user_0.loginname in response.from_detail.loginname
