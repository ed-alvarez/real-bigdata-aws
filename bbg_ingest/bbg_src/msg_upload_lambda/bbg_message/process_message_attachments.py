import logging
import os
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Dict

from bbg_helpers.es_bbg_msg_index import attachment as es_attachment
from bbg_helpers.helper_attachments import AttachmentProcess
from bbg_helpers.helper_file import BBGFileHelper
from bbg_src.msg_upload_lambda.bbg_message.message_helper import xml_to_dict, xstr
from bbg_src.msg_upload_lambda.msg_upload_settings import MSG_GRAPHICS_FILE_EXTENSIONS

from shared.shared_src.tar_file_utils import extract_file_from_tar

log = logging.getLogger()


class ProcessAttachments:
    def __init__(self, attachmentXML: ET, Attachments_FileContent: bytes = None, Attachments_FileName: str = ""):
        self._xml_attachment: ET = attachmentXML
        self._tar_FileName: str = Attachments_FileName
        self._tar_FileContents: bytes = Attachments_FileContent

    # Process the Attachment XML
    def process_attachment(self) -> es_attachment:
        attachment_dict: Dict = xml_to_dict(itemXML=self._xml_attachment)
        attachment_details: es_attachment = es_attachment()

        # Only parse file if there is an actual filename to play with
        if "filename" in attachment_dict:
            attachment_details.filename = attachment_dict["filename"]
            attachment_details.fileid = attachment_dict["fileid"]
            attachment_details.filesize = attachment_dict["filesize"]

            # Set key location to where the file will end up
            tar_file_helper: BBGFileHelper = BBGFileHelper(file=self._tar_FileName)
            attachment_details.tar_file_location = tar_file_helper.file_key

            log.debug(f'file {attachment_dict["filename"]} to retrieve from the Archive')

            file_part, file_extension = os.path.splitext(attachment_dict["filename"])
            if file_extension.lower() in MSG_GRAPHICS_FILE_EXTENSIONS:
                log.debug("Attachment is an image so IGNORING")
                attachment_details.fileB64content = xstr(None)
                attachment_details.error = f'Attachment {attachment_dict["filename"]} is an IMAGE and therefore NOT processed'
            else:
                log.debug("Attachment is NOT an image so trying to retrieve from archive")
                try:
                    b64_content = extract_file_from_tar(
                        file_name_to_extract=attachment_dict["fileid"],
                        tar_file_name=self._tar_FileName,
                        tar_file_contents=self._tar_FileContents,
                    )
                except KeyError as ex:
                    log.error(ex)
                    attachment_details.error = f'cannot extract {attachment_dict["filename"]} from the archive file '
                    return attachment_details
                except ValueError as ex:
                    log.error(ex)
                    attachment_details.error = f"Archive File not present in BBG Manifest"
                    return attachment_details

                if b64_content:
                    attachment_to_parse = AttachmentProcess()
                    attachment_to_parse.inputData = b64_content
                    attachment_to_parse.load_attachment()
                    attachment_to_parse.parse_attachment()
                    attachment_details.content = attachment_to_parse.fileContent
                    del attachment_to_parse

                else:
                    attachment_details.content = xstr(None)
                    attachment_details.error = f'Attachment {attachment_dict["filename"]} cannot be extracted from the archive'

        return attachment_details
