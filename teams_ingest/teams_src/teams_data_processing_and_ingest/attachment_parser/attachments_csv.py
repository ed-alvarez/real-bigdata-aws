import logging

from teams_src.teams_data_processing_and_ingest.attachment_parser.attachments_base import (
    BaseAttachmentProcess,
)

log = logging.getLogger(__name__)


class CSVAttachmentProcess(BaseAttachmentProcess):
    def load_attachment(self):
        """load an attachment string from email and process it ready to pass to Tika server"""
        data_str = self.remove_newlines(data=self._input_data)
        self._file_str = data_str
        # self._file_buffer = self.convert_to_buffer(data=data_str)

    @BaseAttachmentProcess.timer
    def parse_attachment(self):
        self._file_content = self._file_str
