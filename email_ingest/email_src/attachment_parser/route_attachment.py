"""
This class will route the attachment to the relevant attachment decode & process.  returning the attachment part of the elasticsearch record
"""

import logging
import re

import email_settings
from email_helpers.es_email_index_v2 import EMAIL, Attachment, AttachmentsDetail
from email_src.attachment_parser.attachments_csv import CSVAttachmentProcess
from email_src.attachment_parser.attachments_tika import TikaAttachmentProcess

log = logging.getLogger()


class EmailAttachments:
    def __init__(self):
        self._email_msg = None
        self._attachments = EMAIL()

    @property
    def emailMessage(self):
        return self._email_msg

    @emailMessage.setter
    def emailMessage(self, value):
        self._email_msg = value

    @property
    def emailAttachments(self):
        return self._attachments

    @emailAttachments.setter
    def emailAttachments(self, value):
        self._attachments = value

    def parse_attachment(self, file_name, attachment, parser=None, not_yet_implimented_msg=""):
        reformatted_attachment = Attachment()
        if file_name:
            reformatted_attachment.filename = file_name

        if parser:
            attachment_to_parse = parser
            attachment_to_parse.inputData = attachment["payloads"]
            attachment_to_parse.load_attachment()
            attachment_to_parse.parse_attachment()
            v = attachment_to_parse.fileContent
            e = attachment_to_parse.classErrors
            if v:
                value_len = len(v)
                reformatted_attachment.attachment_size = value_len
            if e:
                reformatted_attachment.error = ",".join(e)
            reformatted_attachment["content"] = v
        else:
            reformatted_attachment.error = not_yet_implimented_msg
            reformatted_attachment.content = ""

        return reformatted_attachment

    def return_not_yet_implimented_msg(self, file_part):
        return f"No processing for the {file_part} file type is implimented yet"

    def route_attachment(self, file_name, attachment):
        file_part = file_name.split(".")[-1].lower()
        reformatted_attachment = Attachment()
        parser = None
        ignore_list_members = []
        ignore_list_members.append(email_settings.IGNORE_FILE_EXTENSIONS)
        ignore_list_members.append(email_settings.GRAPHICS_FILE_EXTENSIONS)
        ignore_list_members.append(email_settings.AUDIO_FILE_EXTENSIONS)
        ignore_list_members.append(email_settings.COMPRESSED_FILE_EXTENSIONS)
        ignore_list_members.append(email_settings.ENCRYPTED_FILE_EXTENSIONS)
        ignore_list = [item for sublist in ignore_list_members for item in sublist]

        multi_part_file_extension = file_name.split(".")
        if len(multi_part_file_extension) > 2:
            for part in multi_part_file_extension:
                if len(part) <= 3:
                    if part.lower() in ignore_list:
                        not_yet_implimented_msg = self.return_not_yet_implimented_msg(file_part=part)
                        reformatted_attachment = self.parse_attachment(
                            file_name=file_name,
                            attachment="",
                            not_yet_implimented_msg=not_yet_implimented_msg,
                        )
                        return reformatted_attachment

        else:
            if file_part in ignore_list:
                not_yet_implimented_msg = self.return_not_yet_implimented_msg(file_part=file_part)
                reformatted_attachment = self.parse_attachment(
                    file_name=file_name,
                    attachment=attachment,
                    not_yet_implimented_msg=not_yet_implimented_msg,
                )
                return reformatted_attachment

        if file_part == "csv":
            parser = CSVAttachmentProcess()
            reformatted_attachment = self.parse_attachment(file_name=file_name, attachment=attachment, parser=parser)

        else:
            parser = TikaAttachmentProcess()
            reformatted_attachment = self.parse_attachment(file_name=file_name, attachment=attachment, parser=parser)

        return reformatted_attachment

    def get_attachment_payload_from_email(self, content_types):
        attachment_payloads = list()
        if isinstance(self._email_msg["payloads"], list):
            for individual_payload in self._email_msg["payloads"]:
                if "content-type" in individual_payload["headers"]:
                    if [
                        content_type
                        for content_type in content_types
                        if (content_type in individual_payload["headers"]["content-type"])
                    ]:
                        payload = individual_payload
                        attachment_payloads.append(payload)
                    else:
                        log.debug("No content-type in header maybe a non delivery")
        else:
            if "content-type" in self._email_msg["headers"]:
                if [content_type for content_type in content_types if (content_type in self._email_msg["headers"]["content-type"])]:
                    attachment_payloads.append(self._email_msg)

        return attachment_payloads

    def decode_content_disposition(self, header):
        REGEX = r"""([\r\n\t])"""
        clean_header = re.sub(REGEX, "", header)
        attachment = dict()

        for key in ["filename", "creation-date", "modification-date"]:
            try:
                value = re.search(r'{}=(.*?)(";|$)'.format(key), clean_header).group(1)
            except AttributeError as ex:
                continue
            # value = re.split(r"{}\=(?=;)".format(key), clean_header)
            try:
                attachment[key] = value.replace('"', "")
            except IndexError as ex:
                log.warning(f"In content_disposition_header could not extract {key} from {clean_header}")
                continue

        for key in ["size"]:
            try:
                value = re.search(r"{}=(.*?)(;|$)".format(key), clean_header).group(1)
            except AttributeError as ex:
                continue
            # value = re.split(r"{}\=(?=;)".format(key), clean_header)
            try:
                attachment[key] = value.replace('"', "")
            except IndexError as ex:
                log.warning(f"In content_disposition_header could not extract {key} from {clean_header}")
                continue

        return attachment

    def decode_content_type(self, header):
        REGEX = r"""([\r\n\t])"""
        clean_header = re.sub(REGEX, "", header)
        values = clean_header.split(";")
        attachment = dict()
        for item in values:
            if "/" in item:
                pair = item.split("/")
            elif "=" in item:
                pair = item.split("=")
            attachment[pair[0].strip()] = pair[1].replace('"', "")
        return attachment

    def reformat_attachments(self):
        reformatted_attachments_list = []
        attachments = self.get_attachment_payload_from_email(content_types=["application", "text/csv"])

        for attachment in attachments:
            content_type = {"name": "", "application": ""}
            content_disposition = {"filename": ""}

            if "content-type" in attachment["headers"]:
                content_type = self.decode_content_type(attachment["headers"]["content-type"])

                # choose applications not to process
                if "application" in content_type:
                    content_type_ignore_list = email_settings.CONTENT_TYPE_NOT_TO_PROCESS
                    if [content for content in content_type_ignore_list if (content in content_type["application"])]:
                        log.warning(f'Attachment Type is excluded {attachment["headers"]["content-type"]}')
                        continue
            else:
                log.warning("No content type to parse for name")

            if "content-disposition" in attachment["headers"]:
                content_disposition = self.decode_content_disposition(attachment["headers"]["content-disposition"])
            else:
                log.warning("No content disposition to parse for attachment")

            if "filename" in content_disposition:
                filename_from_headers = content_disposition["filename"]
            elif "name" in content_type:
                filename_from_headers = content_type["name"]
            else:
                log.warning(f"no file name to parse.")
                continue

            file_part = filename_from_headers.split(".")[-1]
            # If the filename includes a > char its n ot an attachment.  This is a best guess after looking at debug
            if ">" in file_part:
                continue

            reformatted_attachment = self.route_attachment(file_name=filename_from_headers, attachment=attachment)
            reformatted_attachments_list.append(reformatted_attachment)

        return reformatted_attachments_list

    def populate_attachments(self):
        attachments_detail = AttachmentsDetail()
        attachments = self.reformat_attachments()

        # attachments = self.reformat_attachments(self._email_msg.attachments)

        if attachments:
            attachments_detail.has_attachment = True
            self._attachments.attachments = attachments
        else:
            attachments_detail.has_attachment = False
            self._attachments.attachments = list()

        self._attachments.attachments_detail = attachments_detail


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
        return email

    def test_meeting_attachment():
        mime_file_id = "hanetf_no_file_in_type"
        attachments = EmailAttachments()
        attachments.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        # attachments.pythonEmailMessage = email_object(file_id=mime_file_id).pythonParsedMIME
        attachments.populate_attachments()
        pprint.pprint(attachments.emailAttachments)

    def test_attachment():
        mime_file_id = "aster_japan"
        attachments = EmailAttachments()
        attachments.emailMessage = email_object(file_id=mime_file_id).parsedMIME
        # attachments.pythonEmailMessage = email_object(file_id=mime_file_id).pythonParsedMIME
        attachments.populate_attachments()
        pprint.pprint(attachments.emailAttachments)

    test_attachment()
