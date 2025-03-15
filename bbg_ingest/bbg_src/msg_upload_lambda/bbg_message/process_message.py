"""
parse a single Bloomberg Message

"""
import re
from datetime import datetime

from bbg_helpers.es_bbg_msg_index import BBG_MSG
from bbg_helpers.es_bbg_msg_index import attachment as es_attachment
from bbg_helpers.es_bbg_msg_index import bloomberg_id
from bbg_helpers.helper_fingerprint import FingerprintHelper
from bbg_src.msg_upload_lambda.bbg_message.message_helper import (
    flaten_address,
    xml_to_dict,
)
from bbg_src.msg_upload_lambda.bbg_message.process_message_attachments import (
    ProcessAttachments,
)
from bbg_src.msg_upload_lambda.msg_upload_settings import ESField, XMLAttrib, XMLitem
from lxml import etree as ET


class ProcessMessage:
    def __init__(
        self,
        emailXML: ET,
        fingerprintMeta: FingerprintHelper,
        Attachments_FileContent: bytes = None,
        Attachments_FileName: str = "",
    ):
        self._xml_email: ET = emailXML
        self._fingerprint_meta: FingerprintHelper = fingerprintMeta
        self._tar_FileName: str = Attachments_FileName
        self._tar_FileContents: bytes = Attachments_FileContent

    def _ignore_attachment(self, attachmentXML: ET) -> bool:
        # TODO do we need to xml_to_dict for the  in statement
        ignore_attachment: bool = True
        attachment_details = xml_to_dict(itemXML=attachmentXML)
        if "reference" in attachment_details:
            ignore_attachment = False
        return ignore_attachment

    def _clean_subject(self, subject_text: str) -> str:
        remove_spaces: str = re.sub(r" {2,}", " ", subject_text)
        remove_chars = remove_spaces.replace("¤", "")
        clean_text = remove_chars.strip()
        return clean_text

    def _clean_body(self, body_text: str) -> str:
        # re.sub(r'\n+', '\n',x)
        remove_newline: str = re.sub(r"\n+", "\n", body_text)
        remove_words: str = re.sub(r".bbScopedStyle\w+", "", remove_newline)
        clean_text = remove_words.strip()
        return clean_text

    def _get_domain(self, email_address: str) -> str:
        if email_address:
            return email_address.split("@")[-1].lower()

    # Iterate an XML user object and turn keys to lower case for ES
    # Expected Children could be FirstName LastName FirmNumber AccountName AccountNumber BloombergUUID
    # BloombergEmailAddress CorporateEmailAddress ClientID1ClientID2
    def _parse_user(self, userXML: ET) -> bloomberg_id:
        user: bloomberg_id = bloomberg_id()
        item: ET
        for item in userXML:
            # Remove the type (to, cc,bcc etc)  from the user data as it's inserted one level up
            if item.tag not in [XMLitem.type.value]:
                if item.text:
                    user[item.tag.lower()] = item.text
        return user

    def _process_es_bbg_user(self, bbguserXML: ET) -> bloomberg_id:
        bbg_user_es: bloomberg_id = bloomberg_id()

        for participant in bbguserXML:
            bbg_user_es = self._parse_user(userXML=participant)

        if getattr(bbg_user_es, "corporateemailaddress"):
            bbg_user_es.domain = self._get_domain(bbg_user_es.corporateemailaddress)
        else:
            bbg_user_es.domain = self._get_domain(bbg_user_es.bloombergemailaddress)

        return bbg_user_es

    # Iterate over an Individual Message Item
    # This holds all the bbg_ib_conversation items Join, Leave, message & attachment
    # The Chiild items can be: MsgID MsgTime MsgTimeUTC MsgLang MsgType OnBehalfOf SharedMessenger OrigSender Sender
    # Recipient Subject Attachment MsgBody DisclaimerReference Greeting
    # @timing
    def process_email(self) -> BBG_MSG:
        email_data: BBG_MSG = BBG_MSG()

        xml_email_part: ET
        for xml_email_part in self._xml_email:

            if xml_email_part.tag == XMLitem.attachment.value:
                # Only process actual attachments not references.  Function ignore attachment fixes
                if self._ignore_attachment(attachmentXML=xml_email_part):
                    attachment_details_obj = ProcessAttachments(
                        attachmentXML=xml_email_part,
                        Attachments_FileName=self._tar_FileName,
                        Attachments_FileContent=self._tar_FileContents,
                    )
                    attachment_details: es_attachment = attachment_details_obj.process_attachment()

                    # Required as using ES Objects
                    existing_value_attachment = getattr(email_data, "attachments")
                    if not existing_value_attachment:
                        existing_value_attachment = list()
                    existing_value_attachment.append(attachment_details)
                    setattr(email_data, "attachments", existing_value_attachment)

                    del attachment_details_obj
                    continue

            if xml_email_part.tag in ["MsgID", "MsgTimeUTC", "MsgLang", "MsgType", "DisclaimerReference"]:
                email_data[xml_email_part.tag.lower()] = xml_email_part.text
                continue

            if xml_email_part.tag == "Greeting":
                email_data.greeting = self._clean_subject(xml_email_part.text)
                continue

            if xml_email_part.tag == "Subject":
                email_data.subject = self._clean_subject(xml_email_part.text)
                continue

            # to be consistent with email
            if xml_email_part.tag == "MsgTime":
                msg_dt = datetime.strptime(xml_email_part.text, "%Y-%m-%d-%H.%M.%S.%f")
                msg_txt = msg_dt.strftime("%Y-%m-%d %H:%M:%S")
                email_data.date = msg_txt
                continue

            # to be consistent with email
            if xml_email_part.tag == "MsgBody":
                email_data.body = self._clean_body(xml_email_part.text)
                continue

            if xml_email_part.tag == XMLitem.sender.value:
                sender_details: bloomberg_id = self._process_es_bbg_user(bbguserXML=xml_email_part)
                email_data.from_detail = sender_details
                email_data.from_ = flaten_address(address=sender_details)

                continue

            if xml_email_part.tag == XMLitem.recipient.value:
                recipient_detail: bloomberg_id = self._process_es_bbg_user(bbguserXML=xml_email_part)
                recipient_flat = flaten_address(recipient_detail)

                key_flat: str = xml_email_part.attrib[XMLAttrib.deliverytype.value].lower()
                key_detail: str = f"{key_flat}_detail"

                # Required as using ES Objects
                existing_value_flat = getattr(email_data, key_flat)
                existing_value_detail = getattr(email_data, key_detail)

                if not existing_value_flat:
                    existing_value_flat = list()
                    existing_value_detail = list()

                existing_value_flat.append(recipient_flat)
                existing_value_detail.append(recipient_detail)

                setattr(email_data, key_detail, existing_value_detail)
                setattr(email_data, key_flat, existing_value_flat)

                continue

            if xml_email_part.tag == XMLitem.origsender.value:
                sender_details = self._process_es_bbg_user(bbguserXML=xml_email_part)
                email_data.from_orig_detail = sender_details
                email_data.from_ = flaten_address(sender_details)
                continue

        # Add an es_id for bulk upload
        # This means process can be re run and Update the ES record rather than overwrite it
        email_data[ESField.id.value] = email_data[ESField.msgid.value]
        self._fingerprint_meta.set_msg_time(msg_time=email_data["date"])

        email_data.fingerprint = self._fingerprint_meta.fingerprint_meta_data

        return email_data
