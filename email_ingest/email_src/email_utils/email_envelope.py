import datetime
import logging
import re
import time
from email.utils import parseaddr
from typing import List

from email_helpers.es_email_index_v2 import EMAIL, Email_Id, MessageIDDetail
from email_settings import (
    CHARS_TO_NOT_SPLIT_EMAIL_NAME,
    EMAIL_SEPARATOR_LIST,
    EMAIL_TO_ADDRESS_NO_DETAIL,
    emailAddress,
    emailName,
)

log = logging.getLogger()


class EmailEnvelope:
    def __init__(self):
        self._email_msg = None
        self._envelope = EMAIL()

    @property
    def emailMessage(self):
        return self._email_msg

    @emailMessage.setter
    def emailMessage(self, value):
        self._email_msg = value

    @property
    def emailEnvelope(self):
        return self._envelope

    @emailEnvelope.setter
    def emailEnvelope(self, value):
        self._envelope = value

    def generate_address_detail_list(self, address_list):
        es_address_detail_list = list()
        for address in address_list:
            es_address_detail = self.generate_address_detail(address)
            es_address_detail_list.append(es_address_detail)
        return es_address_detail_list

    def split_names(self, full_name):
        email_name = emailName()

        # NAME = r"""^([\w\.\-]+)\s*(.+)\s*\b(\w+)$"""
        # parsed_name = re.search(NAME, full_name)
        parsed_name = full_name.split()

        email_name.full = full_name
        email_name.first = parsed_name[0]
        email_name.last = parsed_name[-1]
        return email_name

    def split_email_names(self, full_name):
        email_name = emailName()
        parsed_name = re.split(r"[.-_]", full_name)

        email_name.full = full_name
        email_name.first = parsed_name[0]
        email_name.last = parsed_name[-1]
        return email_name

    def parse_email_names(self, email, address):
        email_name = emailName()
        separator_list = CHARS_TO_NOT_SPLIT_EMAIL_NAME
        if address:

            if [separator for separator in separator_list if (separator in address)]:
                email_name.full = address
                email_name.last = address
                return email_name

            elif " " in address:
                email_name = self.split_names(address)
                return email_name

            else:
                email_name.full = address
                email_name.last = address
                return email_name

        elif email:
            separator_list = EMAIL_SEPARATOR_LIST
            if [separator for separator in separator_list if (separator in email)]:
                email_name = self.split_email_names(email)
                return email_name
            else:
                email_name.full = email
                email_name.last = email
                return email_name

    def format_email_address_string(self, address):
        email_address = emailAddress()

        email_address.email_part = parseaddr(address)[1]

        email_address_split = email_address.email_part.split("@")
        email_address.email_domain = str(email_address_split[-1])
        email_address.email_name = str(email_address_split[0])
        real_name = parseaddr(address)[0]
        if real_name:
            email_address.name_part = real_name
        email_name_parts = self.parse_email_names(email=email_address.email_name, address=email_address.name_part)
        email_address.name_first = getattr(email_name_parts, "first", "")
        email_address.name_last = getattr(email_name_parts, "last", "")
        return email_address

    def generate_address_detail(self, address):
        user = Email_Id()
        if address:
            email_address = self.format_email_address_string(address=address)
            user.corporateemailaddress = email_address.email_part.lower()
            user.firstname = email_address.name_first
            user.lastname = email_address.name_last
            user.domain = email_address.email_domain.lower()
        return user

    def generate_message_id_detail(self):
        message_id_detail = MessageIDDetail()
        message_id_detail.has_thread = False
        message_id_detail.thread_index = None
        message_id_detail.thread_topic = None

        if "thread-index" in self._email_msg["headers"]:
            message_id_detail.thread_index = self._email_msg["headers"]["thread-index"]
            message_id_detail.has_thread = True
        if "thread-topic" in self._email_msg["headers"]:
            message_id_detail.thread_topic = self._email_msg["headers"]["thread-topic"]
            message_id_detail.has_thread = True
        return message_id_detail

    def parse_date_to_fingerprint(self):
        # 'Wed, 11 Dec 2019 12:22:55 -0500'
        pass

    def extract_email_address(self, raw_string: str) -> List:
        email_address_list = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", raw_string)

        # Gmail isn't helpful with its journalling and doesn't have the end
        # user in the headers, but does have the journaling address
        if any("ip-sentinel.net" in s for s in email_address_list):
            email_address_list = []
        return email_address_list

    def parse_recieved_header_list_for_email(self, recieved_header: List) -> str:
        email_addresses: List = []
        emails_str: str = ""
        for item in recieved_header:
            email_addresses.extend(self.extract_email_address(raw_string=item))
        if len(email_addresses) >= 1:
            emails_str = ", ".join(email_addresses)
        return emails_str

    def is_undesclosed_recpient(self, to_email_string: str) -> bool:
        result: bool = False
        separator_list = EMAIL_TO_ADDRESS_NO_DETAIL
        if [separator for separator in separator_list if (separator in to_email_string.lower())]:
            result = True
        return result

    def populate_envelope(self):
        log.debug("Populate envelope")
        if "to" in self._email_msg["headers"]:
            try:
                self._envelope.to = self._email_msg["headers"]["to"]
                extracted_email: str = ""
                undisclosed_recipient: bool = False
                undisclosed_recipient = self.is_undesclosed_recpient(to_email_string=self._envelope.to)

                if undisclosed_recipient:
                    extracted_email = self.parse_recieved_header_list_for_email(self._email_msg["headers"]["received"])
                    if extracted_email:
                        self._envelope.to = extracted_email

                if (extracted_email != "") or (not undisclosed_recipient):
                    to_list: List = self._envelope.to.split(",")
                    self._envelope.to_detail = self.generate_address_detail_list(to_list)

                log.debug(f"populated To: {self._envelope.to}")

            except Exception as ex:
                log.exception(ex)
                log.warning(f"To processing for {self._email_msg['headers']['to']} failed")
                pass

        if "from" in self._email_msg["headers"]:
            try:
                self._envelope.from_ = self._email_msg["headers"]["from"]
                self._envelope.from_detail = self.generate_address_detail(self._envelope.from_)
                log.debug(f"populated From: {self._envelope.from_}")
            except Exception as ex:
                log.exception(ex)
                log.warning(f"From processing for {self._email_msg['headers']['from']} failed")
                pass

        if "cc" in self._email_msg["headers"]:
            try:
                self._envelope.cc = self._email_msg["headers"]["cc"]
                cc_list: List = self._email_msg["headers"]["cc"].split(",")
                self._envelope.cc_detail = self.generate_address_detail_list(cc_list)
                log.debug(f"populated cc: {self._envelope.cc}")
            except Exception as ex:
                log.exception(ex)
                log.warning(f"CC processing for {self._email_msg['headers']['cc']} failed")
                pass
        try:
            bcc_addr = None
            bcc = None
            bcc_bcc = None
            bcc_origRecipient = None

            if "bcc" in self._email_msg["headers"]:
                bcc = self._email_msg["headers"]["bcc"]
            if "x-ms-exchange-organization-originalenveloperecipients" in self._email_msg["headers"]:
                bcc_origRecipient = self._email_msg["headers"]["x-ms-exchange-organization-originalenveloperecipients"]
            if "x-ms-exchange-organization-bcc" in self._email_msg["headers"]:
                bcc_bcc = self._email_msg["headers"]["x-ms-exchange-organization-bcc"]
            bcc_addr = bcc or bcc_bcc or bcc_origRecipient

            # process BCC if there is an entry from the MS x Headers, or if there is no To
            if not self._envelope.to or "undisclosed" in self._envelope.to[0].lower():
                if bcc_addr:
                    if not isinstance(bcc_addr, list):
                        bcc_addr = [bcc_addr]
                    self._envelope.bcc = bcc_addr
                    self._envelope.bcc_detail = self.generate_address_detail_list(self._envelope.bcc)
                    log.debug(f"populated bcc: {self._envelope.bcc}")
        except Exception as ex:
            log.exception(ex)
            log.warning(f"BCC processing failed")
            pass

        try:
            self._envelope.message_id = self._email_msg["headers"]["message-id"]
            self._envelope.message_id_detail = self.generate_message_id_detail()
            log.debug(f"populated Message ID: {self._envelope.message_id}")
        except Exception as ex:
            log.exception(ex)
            log.warning(f"MessageID processing failed")
            pass

        try:
            if "date" in self._email_msg["headers"]:
                email_date = self._email_msg["headers"]["date"]
                date_dt = self.email_date_to_datetime(email_date)
            else:
                date_dt = datetime.datetime.now()
            self._envelope.date = date_dt
        except Exception as ex:
            log.exception(ex)
            log.warning(f"Date processing failed")
            pass

        return

    def email_date_to_datetime(self, email_date):
        # 'Wed, 11 Dec 2019 12:22:55 -0500'
        try:
            t = time.strptime(email_date, "%a, %d %b %Y %H:%M:%S %z")
            d = datetime.datetime.fromtimestamp(time.mktime(t))
        except ValueError:
            d = datetime.datetime.now()
        return d


if __name__ == "__main__":
    import pprint

    from email_ingest.email_src.email_utils.generate_email_obj import parseMIME

    def mime_file(file_id):
        mime_file_to_open = open("/Users/hogbinj/PycharmProjects/emailStep/email_tests/sample_emails/" + str(file_id), "rb")
        msg = mime_file_to_open.read()
        return msg

    def email_object(file_id):
        email = parseMIME()
        email.byteMail = mime_file(file_id=file_id)
        email.process_message()
        return email.parsedMIME

    def test_MIME_Message():
        mime_file_id = "melqart_bcc_2"
        envelope = EmailEnvelope()
        envelope.emailMessage = email_object(file_id=mime_file_id)
        envelope.populate_envelope()
        pprint.pprint(envelope.emailEnvelope)

    test_MIME_Message()
