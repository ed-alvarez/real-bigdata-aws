import base64
import functools
import logging
import re
import timeit

from tika import parser

from shared.shared_src.utils import timing

log = logging.getLogger(__name__)


class AttachmentProcess:
    """This class takes an input from a MIME encoded attachment and seeks to extract any meaningful content from it"""

    def timer(function):
        """A decorator to time a function and add it to the class timing list"""

        @functools.wraps(function)
        def wrap_function(self, *args, **kwargs):
            start_time = timeit.default_timer()
            function(self, *args, **kwargs)
            elapsed = timeit.default_timer() - start_time
            message = 'Function "{name}" took {time:.2f} seconds to complete.'.format(name=function.__name__, time=elapsed)
            self._timers.append(message)
            log.info(message)

        return wrap_function

    @staticmethod
    def remove_newlines(data):
        """Function to remove new line chars from a string"""
        log.debug(data)
        formatted_data = re.sub(r"\r\n", "", data)
        log.debug(formatted_data)
        return formatted_data

    @staticmethod
    def convert_to_buffer(data):
        """Function to convert a string into a Buffer"""
        log.debug(data)
        data_bytes = data.encode("utf-8")
        data_b64 = base64.decodebytes(data_bytes)
        log.debug(data_b64)
        return data_b64

    def __init__(self):
        log.info("initialise Tika File Parse")
        self._input_data = None
        self._file_str = None
        self._file_buffer = None
        self._file_content = None
        self._errors = list()
        self._timers = list()

    @property
    def fileContent(self):
        """fileContent is the tika decoded payload of a document"""
        return self._file_content

    @property
    def inputData(self):
        """inputData is the attachment extract from the MIME file"""
        return self._input_data

    @property
    def classErrors(self):
        """classErrors is a list that contains any errors in the class"""
        return self._errors

    @property
    def classTimers(self):
        """classTimers is a list that contains any function timers in the class"""
        return self._timers

    @inputData.setter
    def inputData(self, value):
        """Class data input"""
        self._input_data = value

    def __str__(self):
        return f"{self._file_content}"

    def __repr__(self):
        return f"{self.__class__.__name__}(" f"{self._input_data!r}, {self._file_content!r})"

    def load_attachment(self):
        """load an attachment string from email and process it ready to pass to Tika server"""
        data_str = self.remove_newlines(data=self._input_data)
        self._file_str = data_str
        self._file_buffer = self.convert_to_buffer(data=data_str)

    @timer
    def parse_attachment(self):
        """pass data to tika server and receive back the decoded document content
        This function should always return an empty string if Tika does not return content or is unreachable"""
        content = ""
        headers = {
            "X-Tika-PDFextractInlineImages": "true",
            "X-Tika-OCRLanguage": "eng",
        }
        try:
            log.info("calling Tika Server")
            # parsed = parser.from_buffer(self._file_buffer, headers=headers, serverEndpoint=settings.TIKA_SERVER_ENDPOINT)
            parsed = parser.from_buffer(self._file_buffer, headers=headers)
        except Exception as ex:
            log.exception(ex)
            self._errors.append(ex)
            pass
        else:
            content = parsed["content"]

        if content:
            content = content.replace("\n\n\n", "")
            content = content.replace("\n\n", "\n")
        self._file_content = content


if __name__ == "__main__":
    test_data_input = "YWJj\r\nZGVmZw=="
    test_data_output_str = "YWJjZGVmZw=="
    test_data_output_buffer = b"abcdef"

    path = "bbg_tests/attachments/ipslogo.txt"
    file = open(path, mode="rt")
    data_input = file.read()
    test_data_input = data_input.replace("\n", "\r\n")
    file.close()

    attachment = AttachmentProcess()
    attachment.inputData = test_data_input
    attachment.load_attachment()
    attachment.parse_attachment()
