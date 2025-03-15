import base64
import functools
import logging
import re
import timeit

import teams_settings

log = logging.getLogger(__name__)


class BaseAttachmentProcess:
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
        if isinstance(data, bytes):
            try:
                data = data.decode("utf-8")
            except UnicodeDecodeError as ex:
                log.warning(f"WARNING Cannot decode string {ex}. Passing raw string through")
                data = "".join(chr(x) for x in data)

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
        self._file_buffer = self._input_data
        return

    def parse_attachment(self):
        return
