"""
-Attachment Processing
    -The BBG Archive file name is extracted from the XML
        -If it is an image file an error field is added and the file extraction/convert is skipped
    -The BBG filename is used to extract the file from the BBG archive TAR
    - The extracted file is B64 encoded and added to the correct ES field for the pipeline
    - The ES ID is generated from the Conversation name plus the iteration number of Attachments and Messages
    - The From is extracted from the XML
    - The To is generated from the Participant list
    - The date/time is captured from the XML
"""
import logging
import os
from io import BytesIO
from typing import List, Tuple

from bbg_helpers.es_bbg_ib_index import BBG_IB
from bbg_helpers.es_bbg_ib_index import attachment as es_attachment
from bbg_helpers.helper_attachments import AttachmentProcess
from bbg_helpers.helper_file import BBGFileHelper
from bbg_src.ib_upload_lambda.bbg_ib_conversation.address_group import msgToGroup
from bbg_src.ib_upload_lambda.bbg_ib_conversation.es_bloomberg_id_helper import (
    create_es_bloomberg_id_from_xml_item,
    flaten_address,
    flaten_list_of_addresses,
)
from bbg_src.ib_upload_lambda.ib_upload_settings import (
    IB_GRAPHICS_FILE_EXTENSIONS,
    XMLitem,
)
from lxml import etree as ET

from shared.shared_src.tar_file_utils import extract_file_from_tar

log = logging.getLogger()


class ProcessSingleAttachment:
    def __init__(
        self,
        attachmentXML: ET,
        attachmentUsers: msgToGroup,
        Attachments_FileName: str = "",
        Attachments_FileContent: bytes = None,
    ) -> None:
        self._attachmentXML: ET = attachmentXML
        self._messageUsers: msgToGroup = attachmentUsers
        self._tar_FileName: str = Attachments_FileName
        self._tar_FileContents: bytes = Attachments_FileContent

    @staticmethod
    def _xstr(s) -> str:
        """Function to convert to string and return a blank if the input is None"""
        return "" if s is None else str(s)

    def _get_file_part_upper(self, filename: str) -> str:
        file_part: str
        file_part, _ = os.path.splitext(filename)
        return file_part.upper()

    def _get_file_extension_lower(self, filename: str) -> str:
        file_extension: str
        _, file_extension = os.path.splitext(filename)
        return file_extension.lower()

    def _is_attachment_a_graphics_file(self, filename: str) -> bool:
        graphics_file: bool = False
        if self._get_file_extension_lower(filename=filename) in IB_GRAPHICS_FILE_EXTENSIONS:
            graphics_file = True
        return graphics_file

    def _get_content(self, es_attachment_detail: es_attachment) -> es_attachment:
        b64_content: str = ""
        filename_in_bbg_tarfile_format: str = self._get_file_part_upper(
            filename=es_attachment_detail.fileid
        ) + self._get_file_extension_lower(filename=es_attachment_detail.fileid)
        log.debug("Attachment is NOT an image so trying to retrieve from archive")

        if self._tar_FileName:
            b64_content = extract_file_from_tar(
                tar_file_name=self._tar_FileName,
                tar_file_contents=self._tar_FileContents,
                file_name_to_extract=filename_in_bbg_tarfile_format,
            )

        if b64_content:
            attachment_to_parse = AttachmentProcess()
            attachment_to_parse.inputData = b64_content
            attachment_to_parse.load_attachment()
            attachment_to_parse.parse_attachment()
            es_attachment_detail.content = attachment_to_parse.fileContent

        else:
            es_attachment_detail.content = self._xstr(None)
            es_attachment_detail.error = f"Attachment {es_attachment_detail.fileid} cannot be extracted from the archive"

        return es_attachment_detail

    def _get_attachment_detail(self, attachment_details: es_attachment) -> es_attachment:
        # Decisions made on the BBG Archive name NOT the actual file name
        log.debug(f"file {attachment_details.fileid} to retrieve from the Archive")

        # Check to see if attachment is capable of being processed
        if self._is_attachment_a_graphics_file(filename=attachment_details.fileid):
            log.debug("Attachment is an image so IGNORING")
            attachment_details.error = f"Attachment {attachment_details.fileid} is an IMAGE and therefore NOT processed"
        else:
            attachment_details = self._get_content(es_attachment_detail=attachment_details)

        tar_file_helper: BBGFileHelper = BBGFileHelper(file=self._tar_FileName)
        attachment_details.tar_file_location = tar_file_helper.file_key

        return attachment_details

    def _generate_list_of_attachment_details(self, attachment_details: es_attachment) -> List[es_attachment]:
        attachment_details: es_attachment = self._get_attachment_detail(attachment_details=attachment_details)
        # Attachment details are always a list of 1 item
        # Turn attachments into a list to be consistent with other message types
        es_attachment_list: List[es_attachment] = list(es_attachment())
        es_attachment_list.append(attachment_details)
        return es_attachment_list

    def _create_es_BBG_IB_from_XML(self, attachmentXML: ET, messageUsers: msgToGroup) -> Tuple[BBG_IB, es_attachment]:
        attachment_item: BBG_IB = BBG_IB()
        attachment_details: es_attachment = es_attachment()

        attachment: ET
        for attachment in self._attachmentXML:
            if attachment.tag in ["FileName", "FileID", "FileSize"]:
                setattr(attachment_details, attachment.tag.lower(), attachment.text)
                continue

            # The Attachment User is the FROM
            elif attachment.tag == XMLitem.user.value:
                user = create_es_bloomberg_id_from_xml_item(userXML=attachment)
                attachment_item.from_detail = user
                attachment_item.from_ = flaten_address(user)
                continue

            else:
                setattr(attachment_item, attachment.tag.lower(), attachment.text)

        return attachment_item, attachment_details

    # Process the Attachment XML
    def process_attachment(self) -> BBG_IB:

        attachment_details: es_attachment
        attachment_item: BBG_IB
        attachment_item, attachment_details_base = self._create_es_BBG_IB_from_XML(
            attachmentXML=self._attachmentXML, messageUsers=self._messageUsers
        )
        attachment_item.attachments = self._generate_list_of_attachment_details(attachment_details=attachment_details_base)
        attachment_item.to_detail = self._messageUsers.get_to_list(messageFrom=attachment_item.from_detail)
        attachment_item.to = flaten_list_of_addresses(attachment_item.to_detail)

        return attachment_item
