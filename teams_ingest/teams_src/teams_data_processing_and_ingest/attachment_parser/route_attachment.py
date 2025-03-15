"""
This class will route the attachment to the relevant attachment decode & process.  returning the attachment part of the elasticsearch record
"""

import logging
from typing import Dict, List, Optional

import teams_settings
from teams_src.teams_data_processing_and_ingest.attachment_parser.attachments_csv import (
    CSVAttachmentProcess,
)
from teams_src.teams_data_processing_and_ingest.attachment_parser.attachments_tika import (
    TikaAttachmentProcess,
)
from teams_src.teams_data_processing_and_ingest.elastic_search.es_teams_index import (
    attachment as ES_Attachment,
)
from teams_src.teams_data_processing_and_ingest.teams_conversation import (
    attachment_helper_functions,
)
from teams_src.teams_shared_modules.teams_data_classes import ClientCreds

log = logging.getLogger()


class TeamsAttachmentDecode:
    def __init__(self, teams_attachment: Dict, client_creds: ClientCreds) -> None:
        self._teams_attachment: Dict = teams_attachment
        self._attachment_bytes: Optional[bytes] = None
        self._client_creds: ClientCreds = client_creds

    @property
    def attachmentBytes(self) -> bytes:
        return self._attachment_bytes

    def _parse_attachment(self, file_name, parser=None, not_yet_implimented_msg="") -> ES_Attachment:
        reformatted_attachment = ES_Attachment()

        self._attachment_bytes: bytes = attachment_helper_functions.get_attachment_data(
            url=self._teams_attachment["contentUrl"], client_creds=self._client_creds
        )

        if file_name:
            reformatted_attachment.filename = file_name

        if parser and self._attachment_bytes and not not_yet_implimented_msg:
            attachment_to_parse = parser
            attachment_to_parse.inputData = self._attachment_bytes
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

    def _return_not_yet_implimented_msg(self, file_part):
        return f"No processing for the {file_part} file type is implimented yet"

    def route_attachment(self) -> ES_Attachment:
        file_name: str = self._teams_attachment["name"]
        log.debug(f"Attachment File Name = {file_name}")
        file_part: str = ""
        try:
            file_part = file_name.split(".")[-1].lower()
            log.debug(f"Attachment File Part = {file_part}")
        except ValueError or AttributeError:
            log.error(f"File Name {file_name} has no file part")
            pass
        reformatted_attachment: ES_Attachment = ES_Attachment()
        parser = None
        ignore_list_members: List[str] = []
        ignore_list_members.append(teams_settings.IGNORE_FILE_EXTENSIONS)
        ignore_list_members.append(teams_settings.GRAPHICS_FILE_EXTENSIONS)
        ignore_list_members.append(teams_settings.AUDIO_FILE_EXTENSIONS)
        ignore_list_members.append(teams_settings.COMPRESSED_FILE_EXTENSIONS)
        ignore_list_members.append(teams_settings.ENCRYPTED_FILE_EXTENSIONS)
        ignore_list: List[str] = [item for sublist in ignore_list_members for item in sublist]

        multi_part_file_extension = file_name.split(".")
        if len(multi_part_file_extension) > 2:
            for part in multi_part_file_extension:
                if len(part) <= 3:
                    if part.lower() in ignore_list:
                        log.debug("Not Yet Implimented parser")
                        not_yet_implimented_msg = self._return_not_yet_implimented_msg(file_part=part)
                        reformatted_attachment = self._parse_attachment(
                            file_name=file_name,
                            not_yet_implimented_msg=not_yet_implimented_msg,
                        )
                        return reformatted_attachment

        else:
            if file_part in ignore_list:
                log.debug("Not Yet Implimented parser")
                not_yet_implimented_msg = self._return_not_yet_implimented_msg(file_part=file_part)
                reformatted_attachment = self._parse_attachment(file_name=file_name, not_yet_implimented_msg=not_yet_implimented_msg)
                return reformatted_attachment

        if file_part == "csv":
            log.debug("CSV parser")
            parser = CSVAttachmentProcess()
            reformatted_attachment = self._parse_attachment(file_name=file_name, parser=parser)

        else:
            parser = TikaAttachmentProcess()
            log.debug("Tika parser")
            reformatted_attachment = self._parse_attachment(file_name=file_name, parser=parser)
            if reformatted_attachment:
                log.debug(f"Tika extracted some contents from {file_name}")
            else:
                log.warning(f"Tika could not extract data from {file_name}")
        return reformatted_attachment


if __name__ == "__main__":
    pass
