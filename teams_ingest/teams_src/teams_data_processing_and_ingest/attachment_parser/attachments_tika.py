import logging
import re

from teams_src.teams_data_processing_and_ingest.attachment_parser.attachments_base import (
    BaseAttachmentProcess,
)
from tika import parser

log = logging.getLogger(__name__)


class TikaAttachmentProcess(BaseAttachmentProcess):

    # def load_attachment(self):
    #    """load an attachment string from email and process it ready to pass to Tika server"""
    #    data_str = self.remove_newlines(data=self._input_data)
    #    self._file_str = data_str
    #    self._file_buffer = self.convert_to_buffer(data=data_str)

    @BaseAttachmentProcess.timer
    def parse_attachment(self):
        """pass data to tika server and receive back the decoded document content
        This function should always return an empty string if Tika does not return content or is unreachable"""
        content = ""
        headers = {
            "X-Tika-PDFextractInlineImages": "true",
            "Content-type": "image/png",
            "X-Tika-OCRLanguage": "eng",
        }
        try:
            log.info("calling Tika Server")
            parsed = parser.from_buffer(self._file_buffer, headers=headers)
        except Exception as ex:
            log.warning(ex)
            self._errors.append(str(ex.args[0]))
            pass
        else:
            content = parsed["content"]

        clean_content = ""
        if content:
            clean_content = re.sub(r"\n\s*\n", "\n\n", content)
        self._file_content = clean_content
