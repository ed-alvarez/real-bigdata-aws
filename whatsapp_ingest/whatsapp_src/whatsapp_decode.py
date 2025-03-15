import base64
import datetime
import logging
import struct
import sys
from email import policy
from email.message import EmailMessage
from email.parser import Parser
from typing import Dict, List, Tuple

import emoji
from mailparser import MailParser, parse_from_string
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from whatsapp_ingest import whatsapp_settings
from whatsapp_ingest.whatsapp_helpers.es_whatsapp_index import (
    WHATSAPP,
    Attachment,
    AttachmentDetail,
    BodyDetail,
    Fingerprint_Meta,
    MessageIDDetail,
    SubjectDetail,
    Whatsapp_Id,
)
from whatsapp_ingest.whatsapp_helpers.helper_image_attachments import (
    ImageAttachmentProcess,
)

log = logging.getLogger()


class whatsappParser:
    def __init__(self, email_body: str, fingerprint_meta: Fingerprint_Meta):
        self._mime_content = email_body
        self._mime_decode = MailParser
        self._whatsapp_data = dict()
        self._fingerprint_meta = fingerprint_meta
        self._es_whatsapp: WHATSAPP = WHATSAPP()
        self._python_body = str()

    @property
    def esWhatsApp(self):
        return self._es_whatsapp

    @staticmethod
    def _generate_whatsapp_id_from_email_addr(address_part):
        addresses = list()
        for addr in address_part:
            if addr:
                user = Whatsapp_Id()
                user.corporateemailaddress = addr[1]
                names = addr[0].split()
                user.whatsapp_id = names[0]
                domain = addr[1].split("@")[-1]
                user.domain = str(domain).lower()
                addresses.append(user)
        return addresses

    @staticmethod
    def _generate_es_to_from_email_addr(address_part: List) -> List:
        to_addresses: List = list()
        item: Tuple
        for item in address_part:
            to_addresses.append(item[1])
        return to_addresses

    @staticmethod
    def reformat_attachments(attachments: List) -> List[Attachment]:
        reformatted_attachments_list = []
        attachment: Dict
        for attachment in attachments:
            attachment_type = attachment["mail_content_type"].split("/")[0]
            file_part = attachment["filename"].split(".")[-1]

            reformatted_attachment: Attachment = Attachment()
            if attachment_type != "":
                for k, v in attachment.items():
                    if k in ["payload"]:
                        if k == "payload":
                            k = "content"
                            attachment_to_parse = ImageAttachmentProcess()
                            attachment_to_parse.inputData = v
                            attachment_to_parse.load_attachment()
                            attachment_to_parse.parse_image_attachment()
                            v = attachment_to_parse.fileContent
                            if v:
                                value_len = len(v)
                                reformatted_attachment.attachment_size = value_len
                                reformatted_attachment[k] = v
                            else:
                                reformatted_attachment.error = f'No data can be extracted from {attachment["filename"]}'
            else:
                reformatted_attachment.error = f"No Parser for {attachment_type} filetype .{file_part} available"

            reformatted_attachment.filename = attachment["filename"]
            reformatted_attachment.type = attachment["mail_content_type"].split("/")[0]
            reformatted_attachment.sub_type = attachment["mail_content_type"].split("/")[-1]
            reformatted_attachments_list.append(reformatted_attachment)
        return reformatted_attachments_list

    def parse_email_to_es_whatsapp(self) -> WHATSAPP:
        es_whatsapp: WHATSAPP = WHATSAPP()
        mime_data: MailParser = self._parse_mime_message_to_dict(mime_content=self._mime_content)
        original_body: str = self._get_email_payload(mime_content=self._mime_content)
        whatsapp_data: Dict = self._extract_whatsapp_data(mime_decode=mime_data)
        es_whatsapp = self._populate_es_whatsapp_record(whatsapp_data=whatsapp_data, original_body=original_body)
        es_whatsapp.fingerprint = self._update_fingerprint_meta(fingerprint_meta=self._fingerprint_meta, whatsapp_data=whatsapp_data)
        self._es_whatsapp = es_whatsapp
        return es_whatsapp

    def _update_fingerprint_meta(self, fingerprint_meta: Fingerprint_Meta, whatsapp_data: Dict) -> Fingerprint_Meta:
        fingerprint_meta: Fingerprint_Meta = fingerprint_meta
        fingerprint_meta.time = whatsapp_data["date"]
        return fingerprint_meta

    def _parse_mime_message_to_dict(self, mime_content: str) -> MailParser:
        try:
            mime_decode: MailParser = parse_from_string(mime_content)
        except Exception as ex:
            log.exception(f"{ex.__class__.__name__}: ERROR extracting MIME contents: {ex}")
            error_type, error_instance, traceback = sys.exc_info()
            raise error_type(error_instance.info).with_traceback(traceback)
        return mime_decode

    def _get_email_payload(self, mime_content: str) -> str:
        python_body: str = ""
        try:
            email_parser: Parser = Parser(policy=policy.default)
            python_mail: EmailMessage = email_parser.parsestr(mime_content)
        except Exception as ex:
            log.error("Cannot Parse Data with Python MIME API")
            error_type, error_instance, traceback = sys.exc_info()
            raise error_type(error_instance.info).with_traceback(traceback)
        try:
            python_payload: EmailMessage = python_mail.get_payload()[0]
        except Exception as ex:
            log.error("Cannot extract a Payload from the original email")
            error_type, error_instance, traceback = sys.exc_info()
            raise error_type(error_instance.info).with_traceback(traceback)
        try:
            python_body = python_payload.get_payload()
        except:
            log.error("Cannot extract a Body from the Payload ")
            error_type, error_instance, traceback = sys.exc_info()
            raise error_type(error_instance.info).with_traceback(traceback)

        return python_body

    def _extract_whatsapp_data(self, mime_decode: MailParser) -> Dict:
        whatsapp_data: Dict = {}

        for header_key, header_value in mime_decode.headers.items():
            if header_key in whatsapp_settings.WHATSAPP_KEYS:
                whatsapp_data[header_key.lower()] = header_value

        for key in whatsapp_settings.MIME_KEYS:
            whatsapp_data[key.lower()] = getattr(mime_decode, key.lower())

        return whatsapp_data

    def _populate_es_whatsapp_record(self, whatsapp_data: Dict, original_body: str) -> WHATSAPP:
        es_whatsapp: WHATSAPP = WHATSAPP()
        es_whatsapp.to = self._generate_es_to_from_email_addr(address_part=whatsapp_data["to"])
        es_whatsapp.to_detail = self._generate_whatsapp_id_from_email_addr(whatsapp_data["to"])
        es_whatsapp.from_ = whatsapp_data["from"][0][1]
        es_whatsapp.from_detail = self._generate_whatsapp_id_from_email_addr(whatsapp_data["from"])[0]
        es_whatsapp.date = whatsapp_data["date"]
        es_whatsapp.message_id_details = self._populate_MessageIDDetail(whatsapp_data=whatsapp_data)

        es_whatsapp.body = self._populate_body(original_body=original_body, plain_body=whatsapp_data["body"])
        es_whatsapp.body_detail = self._populate_body_detail(es_body=es_whatsapp.body)
        es_whatsapp.subject = whatsapp_data["subject"]
        es_whatsapp.subject_detail = self._populate_subject_detail(es_subject=es_whatsapp.subject)
        es_whatsapp.attachments = self.reformat_attachments(whatsapp_data["attachments"])
        es_whatsapp.attachments_detail = self._populate_attachment_detail(es_attachment=es_whatsapp.attachments)

        return es_whatsapp

    def _populate_MessageIDDetail(self, whatsapp_data: Dict) -> MessageIDDetail:
        message_id_detail: MessageIDDetail = MessageIDDetail()
        message_id_detail.group_name = whatsapp_data["x-telemessage-group_name"]
        message_id_detail.group_id = whatsapp_data["x-telemessage-groupid"]
        message_id_detail.message_id = whatsapp_data["x-telemessage-archivemessageid"]
        if "x-telemessage-thread_id" in whatsapp_data:
            message_id_detail.thread_index = whatsapp_data["x-telemessage-thread_id"]
            message_id_detail.has_thread = True
        else:
            message_id_detail.has_thread = False
        return message_id_detail

    def _populate_body(self, original_body: str, plain_body: str) -> str:
        es_body: str = ""
        try:
            es_body = emoji.demojize(original_body)
        except:
            log.warning("cannot de-emoji body")
            es_body = original_body
            pass

        if not es_body:
            es_body = plain_body
        return es_body

    def _populate_body_detail(self, es_body: str) -> BodyDetail:
        es_body_detail: BodyDetail = BodyDetail()
        es_body_detail.has_body = False
        if es_body:
            sid: SentimentIntensityAnalyzer = SentimentIntensityAnalyzer()
            es_body_detail.body_sentiment = sid.polarity_scores(es_body)
            es_body_detail.body_size = len(es_body)
            es_body_detail.has_body = True
            del sid
        return es_body_detail

    def _populate_subject_detail(self, es_subject: str) -> SubjectDetail:
        es_subject_detail: SubjectDetail = SubjectDetail()
        es_subject_detail.has_subject = False
        if es_subject:
            sid: SentimentIntensityAnalyzer = SentimentIntensityAnalyzer()
            es_subject_detail.has_subject = True
            es_subject_detail.subject_sentiment = sid.polarity_scores(es_subject)
            del sid
        return es_subject_detail

    def _populate_attachment_detail(self, es_attachment: List[Attachment]) -> AttachmentDetail:
        es_attachment_detail: AttachmentDetail = AttachmentDetail()
        es_attachment_detail.has_attachment = False
        if es_attachment_detail:
            es_attachment_detail.has_attachment = True
        return es_attachment_detail

    @staticmethod
    def parse_thread_index(index: "str") -> Tuple:

        s = base64.b64decode(index)

        # real guids are in this format
        guid = struct.unpack(">IHHQ", s[6:22])
        guid = "%08X-%04X-%04X-%04X-%12X" % (
            guid[0],
            guid[1],
            guid[2],
            (guid[3] >> 48) & 0xFFFF,
            guid[3] & 0xFFFFFFFFFFFF,
        )

        # ours are just md5 digests
        # guid = binascii.hexlify(s[6:22])

        date_data = s[3:9] + b"\0\0"
        pre_f = struct.unpack(">Q", date_data)
        f = pre_f[0]
        micro_f = f // 1000
        time_delta = datetime.timedelta(microseconds=micro_f)
        ts = [datetime.datetime(1601, 1, 1) + time_delta]

        # pick out the 5 byte suffixes for used a Reply-To and the timeshift
        for n in range(22, len(s), 5):
            f = struct.unpack(">I", s[n : n + 4])[0]
            ts.append(ts[-1] + datetime.timedelta(microseconds=(f << 18) // 10))

        return guid, ts
