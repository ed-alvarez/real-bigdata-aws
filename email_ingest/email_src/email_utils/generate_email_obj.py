import logging
import re
from email.header import decode_header, make_header
from email.utils import formataddr, parseaddr
from typing import Dict, List

from email_helpers.ips_tools import decode_from_utf8
from email_settings import GMAIL_DOMAIN_LIST
from salmon.encoding import EncodingError, from_string, properly_decode_header

log = logging.getLogger()
ESCAPES: str = "".join([chr(char) for char in range(1, 32)])
TRANSLATOR: Dict = str.maketrans("", "", ESCAPES)


class parseMIME:
    """
    This class takes a raw email and using the salmon email libary returns a dictionary of all values
    The transform handles Gmail and Exchange Journaled emails
    The output is Headers & Payload,

    Other than splitting addresses into a list no formatting of data is undertaken.

    """

    def __init__(self):
        self._byte_mail = None
        self._email = None

    @property
    def byteMail(self):
        return self._byte_mail

    @byteMail.setter
    def byteMail(self, value):
        self._byte_mail = value

    @property
    def parsedMIME(self):
        return self._email

    def remove_non_ascii_chars(self, string):
        clean_string = string
        try:
            clean_string = string.encode().decode("ascii", errors="ignore")
        except TypeError as ex:
            pass
        return clean_string

    def clean_header_text(self, header):
        clean_header = header

        if not isinstance(header, str):
            header = header.__str__()

        # if '?utf-8?' in header:
        try:
            header = decode_from_utf8(decode=header)
        except Exception as ex:
            log.warning(f"Header UTF8 Decode Failed")
            raise ex

        header = self.remove_non_ascii_chars(string=header)

        REGEX = r"(?<=\?=)((?:\r\n|[\r\n])[\t ]+)(?==\?)"
        try:
            clean_header = re.sub(REGEX, "", header).strip()
        except TypeError as ex:
            pass

        return clean_header

    def remove_control_chars(self, dirty_string: str) -> str:
        # https://stackoverflow.com/questions/8115261/how-to-remove-all-the-escape-sequences-from-a-list-of-strings
        try:
            clean_string: str = dirty_string.translate(TRANSLATOR)
        except AttributeError as ex:
            log.exception(ex)
        return clean_string

    def clean_header_list(self, dirty_header: List, key: str) -> List:
        clean_header: List = []
        for item in dirty_header:
            clean_item: str = self.clean_header_item_str(dirty_header_item=item, key=key)
            clean_header.append(clean_item)
        return clean_header

    def clean_header_item_str(self, dirty_header_item: str, key: str) -> str:
        clean_header_item: str = ""
        header_item_sting_to_clean: str = dirty_header_item

        # If there is nothing to clean then don't try to clean it!
        if not header_item_sting_to_clean:
            return dirty_header_item

        header_item_sting_to_clean = self.remove_control_chars(dirty_string=header_item_sting_to_clean)

        try:
            clean_header_item = str(make_header(decode_header(header_item_sting_to_clean)))
        except (UnicodeDecodeError, EncodingError, LookupError) as ex:
            log.warning(f"{key} Pass 1 header {header_item_sting_to_clean} did not clean")
            pass

        if not clean_header_item:
            try:
                clean_header_item = properly_decode_header(header_item_sting_to_clean)
            except (UnicodeDecodeError, EncodingError) as ex:
                log.warning(f"{key} Pass 2 header {header_item_sting_to_clean} did not clean")
                pass

        if not clean_header_item:
            try:
                clean_header_item = self.clean_header_text(header_item_sting_to_clean)
            except (UnicodeDecodeError, EncodingError) as ex:
                log.warning(f"{key} Pass 3 header {header_item_sting_to_clean} did not clean")
                pass

        if not clean_header_item:
            clean_header_item = header_item_sting_to_clean

        return clean_header_item

    def headers_to_dict(self, key_list: List, mail_obj) -> Dict:
        headers: Dict = {}
        key_set: set = set(key_list)
        for key in key_set:
            try:
                header_result = mail_obj.get_all(key)
            except Exception as ex:
                log.exception(ex)
                raise ex
            if len(header_result) > 1:
                header = self.clean_header_list(header_result, key=key)
            else:
                header = self.clean_header_item_str(str(header_result[0]), key=key).strip()
            headers[key.lower()] = header
        return headers

    def process_payloads(self, email_payload, email_payload_header):
        if email_payload.parts:
            payloads = list()
            for payload_part in email_payload.parts:
                payload_keys = payload_part.keys()
                payload_header_dict = self.headers_to_dict(key_list=payload_keys, mail_obj=payload_part)
                try:
                    payload_body = payload_part.body
                except Exception as ex:
                    log.warning(f"Payload Part decode error trying raw string {ex}")
                    try:
                        payload_body = payload_part.mime_part._payload
                    except Exception as ex:
                        log.warning(f"Payload Part raw string error {ex}")
                        payload_body = ""

                payload_part = {"headers": payload_header_dict, "payloads": payload_body}
                payloads.append(payload_part)
        else:
            try:
                payloads = email_payload.body
            except Exception as ex:
                log.warning(f"payload cannot be decoded {ex}")
                payloads = ""

        return {"headers": email_payload_header, "payloads": payloads}

    def process_mime_message(self, email_message, email_message_headers: Dict) -> Dict:
        payloads: List = []
        processed_email_message: Dict = {}
        processed_email_message["headers"]: Dict = email_message_headers
        processed_email_message["payloads"]: List = []
        for part in email_message.walk():
            keys = part.keys()
            try:
                part_header_dict = self.headers_to_dict(key_list=keys, mail_obj=part)
            except EncodingError as ex:
                log.exception(ex)
                pass
            email_part = self.process_payloads(email_payload=part, email_payload_header=part_header_dict)
            processed_email_message["payloads"].append(email_part)

        # processed_email_message["payloads"] = payloads
        return processed_email_message

    def create_payload_from_message(self, body, content_type):
        new_header = dict()
        new_header["content-type"] = content_type
        new_header["content-transfer-encoding"] = "base64"
        new_payload = {"headers": new_header, "payloads": body}
        return new_payload

    def clean_address_string(self, raw_address: str) -> str:
        updated_address: str = raw_address
        address_non_print_char_removed = self.remove_control_chars(dirty_string=raw_address)
        clean_address = re.sub(r'(")', "", address_non_print_char_removed)
        address_parts = parseaddr(clean_address)
        if "?utf-8?" in address_parts[0]:
            try:
                decoded_real_name = decode_from_utf8(decode=address_parts[0])
                updated_address = formataddr({decoded_real_name, address_parts[1]})
            except Exception as ex:
                log.warning(f"email {raw_address} did not clean")
                pass
        else:
            updated_address = clean_address

        return updated_address

    def clean_address_list(self, raw_address: List) -> List:
        clean_address_list: List = []
        for item in raw_address:
            clean_address_list.append(self.clean_address_string(item))
        return clean_address_list

    def parse_email_addresses(self, header_dict: Dict) -> Dict:
        my_list_set: set = {"to", "cc", "bcc", "from"}
        my_dict_set: set = set(header_dict)

        for key in my_list_set.intersection(my_dict_set):
            raw_address_str: str = header_dict[key]
            clean_address_str: str = self.clean_address_string(raw_address_str)
            address_list: List = clean_address_str.split(",")
            clean_address_list: List = [x.strip(" ") for x in address_list]
            header_dict[key] = ", ".join(clean_address_list)

        return header_dict

    def process_message(self):
        email_object = self.load_mail_to_object(byte_string=self._byte_mail)
        journaled_email = self.extract_journaled_message(mail_obj=email_object)
        keys = journaled_email.keys()
        raw_header_dict = self.headers_to_dict(key_list=keys, mail_obj=journaled_email)
        header_dict = self.parse_email_addresses(raw_header_dict)

        try:
            decode_body = journaled_email.body
        except:
            decode_body = journaled_email.mime_part._payload

        if decode_body:
            new_payload = self.create_payload_from_message(body=decode_body, content_type=header_dict["content-type"])
            result = {
                "headers": header_dict,
                "payloads": [
                    new_payload,
                ],
            }
        else:
            try:
                result = self.process_mime_message(email_message=journaled_email, email_message_headers=header_dict)
            except Exception as ex:
                log.exception(ex)
                raise (ex)

        self._email = result

        return result

    def load_mail_to_object(self, byte_string):
        try:
            email_message = from_string(byte_string)
            # email_message = Parser(policy=custom_policy).parsestr(byte_string.decode())
        except Exception as ex:
            error_message = "Raw Email String load Fail"
            log.exception("Raw Email String load Fail")
            raise Exception(error_message)
        return email_message

    def is_from_Gmail(self, mail_obj):
        from_gmail = False
        provider = mail_obj.get_all("Received")
        source = provider[0]
        # Detect if email comes from a GMail domain
        domain_list = GMAIL_DOMAIN_LIST
        if [domain for domain in domain_list if (domain in source)]:
            from_gmail = True
        return from_gmail

    def extract_journaled_message(self, mail_obj):
        if self.is_from_Gmail(mail_obj=mail_obj):
            return mail_obj
        else:
            journal_mail = mail_obj.parts[1]
            journaled_email = journal_mail.parts[0]
            return journaled_email


if __name__ == "__main__":
    import pprint

    def mime_file(file_id):
        mime_file_to_open = open("/Users/hogbinj/PycharmProjects/emailStep/email_tests/sample_emails/" + str(file_id), "rb")
        msg = mime_file_to_open.read()
        return msg

    def email_object(file_id):
        email = parseMIME()
        email.byteMail = mime_file(file_id=file_id)
        try:
            email.process_message()
        except Exception as ex:
            log.exception(ex)
        return email.parsedMIME

    def simple_MIME():
        mime_file_id = "aster_japan"
        output = email_object(file_id=mime_file_id)
        pprint.pprint(output)

    simple_MIME()
