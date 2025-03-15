"""
this class
- loads the XML file and archive file from the local /tmp directory
- Iterates the XML tree and only processes Conversations
- The bbg_ib_conversation is passed to the ElasticSearch Bulk upload Module

The self generated ES_ID means that the process can be re-run without creating a whole new set of data in the Search
cluster
"""

import logging
from io import BytesIO
from itertools import islice

from aws_lambda_context import LambdaContext
from bbg_helpers.helper_file import BBGFileHelper
from bbg_helpers.helper_fingerprint import FingerprintHelper
from bbg_src.ib_upload_lambda.bbg_ib_conversation.conversation_bulk_object import (
    ibConversation,
)
from bbg_src.ib_upload_lambda.bbg_ib_conversation.process_single_conversation import (
    ProcessConversation,
)
from bbg_src.ib_upload_lambda.ib_upload_settings import (
    IB_AWS_TIMEOUT_MILLISECONDS,
    IB_ES_SCHEMA,
    XMLitem,
)
from lxml import etree as ET
from lxml.etree import ParseError, XMLParser

from shared.shared_src.s3.s3_helper import S3Helper
from shared.shared_src.utils import timing

log = logging.getLogger()


class ParseBBGXMLtoES:
    def __init__(
        self,
        ib_FileName: str,
        ib_FileContents: bytes,
        awsContext: LambdaContext,
        xmlRecordNumber: int,
        tar_FileName: str,
        tar_FileContents: bytes,
        S3_helper: S3Helper,
    ):

        self._ib_FileName: str = ib_FileName
        self._ib_FileContents: bytes = ib_FileContents
        self._tar_FileName: str = tar_FileName
        self._tar_FileContents: bytes = tar_FileContents
        self._s3_obj: S3Helper = S3_helper
        self._xml_iteration_start_item: int = xmlRecordNumber
        self._aws_context: LambdaContext = awsContext

        self._fingerprint_meta: FingerprintHelper = FingerprintHelper()

        self._bucket_name: str = str()
        self._client_name: str = str()

        self._es_index: str = str()
        self._es_pipeline: str = str()

        self._xml_iteration_item: int = 0

        self._tree: ET = None
        self._root: ET = None
        self._xml_parse_complete: bool = False
        # Set to false for Step function.  Only set to true when XML has finished processing

    @property
    def xmlParseComplete(self) -> bool:
        return self._xml_parse_complete

    @property
    def xmlItemNextStart(self) -> int:
        return self._xml_iteration_item

    def initialise_variables(self):
        self._bucket_name = self._s3_obj.bucketName
        self._client_name = self._s3_obj.clientName
        parser: XMLParser = XMLParser(recover=True)
        try:
            self._tree = ET.parse(BytesIO(self._ib_FileContents), parser=parser)
        except ParseError as ex:
            log.exception(ex)
            log.error(f"Cannot open the XML file {self._ib_FileName}")
            raise ex
        self._root = self._tree.getroot()

        self._fingerprint_meta.set_client_name(client_name=self._client_name)

        file_helper: BBGFileHelper = BBGFileHelper(file=self._ib_FileName)
        self._fingerprint_meta.set_key_name(key_name=file_helper.file_key)
        self._fingerprint_meta.set_bucket_name(bucket_name=self._bucket_name)
        self._fingerprint_meta.set_msg_type(msg_type="bbg.im")
        self._fingerprint_meta.set_schema(IB_ES_SCHEMA)

    def _has_time_limit_been_reached(self, time_remaining: int) -> bool:
        if time_remaining <= IB_AWS_TIMEOUT_MILLISECONDS:
            log.info(f"Loop Limit: TIME {time_remaining} is less than {IB_AWS_TIMEOUT_MILLISECONDS}")
            return True
        else:
            return False

    # Work out from the XML if to skip a branch of the XML tree
    # Order is important and works from MOST specific (topic, from etc) to LEAST specific (XML Type)
    # Returns TRUE to skip. Defaults to False
    def _skip_this_node(self, level1XML) -> bool:
        skip_this: bool = False
        """
        if level1XML.attrib[XMLattr.roomtype.value] == 'C':
            skip_this = True
            return skip_this
        """
        # Is the record type a Conversation (this gets rid of BBG XML file header
        if level1XML.tag != XMLitem.conversation.value:
            skip_this = True
            return skip_this
        return skip_this

    @timing
    def xml_step(self) -> None:
        log.info(f"Start XML Iteration at item: {self._xml_iteration_start_item}")
        loop_x: int
        level_1: ET
        for loop_x, level_1 in enumerate(islice(self._root, self._xml_iteration_start_item, None)):
            self._xml_iteration_item = self._xml_iteration_start_item + loop_x
            log.info(f"XML conversation to be processed: {self._xml_iteration_item}")

            # test to see if this node should be processed
            if self._skip_this_node(level1XML=level_1):
                continue

            process_conversation_obj: ProcessConversation = ProcessConversation(
                conversationXML=level_1,
                awsLambdaContext=self._aws_context,
                Attachments_FileName=self._tar_FileName,
                Attachments_FileContent=self._tar_FileContents,
                fingerprintMeta=self._fingerprint_meta,
            )
            conversation: ibConversation = process_conversation_obj.process_conversation()

            # Check the time left from the lambda context.
            time_remaining: int = self._aws_context.get_remaining_time_in_millis()

            # If the bbg_ib_conversation processing has timed out then exit the XML processing loop
            # We do not update the XML item number as we still have some processing to do in this item
            if self._has_time_limit_been_reached(time_remaining=time_remaining):
                self._xml_parse_complete = False
                return

            log.info(f"{time_remaining / 1000} seconds left. Time for another bbg_ib_conversation")

            # increment the XML record number so that the Next return is correctnumber
            self._xml_iteration_item += 1

            del process_conversation_obj
            del conversation

        # If True then there is NO more XML to parse.  This value will be tested in the Step function loop
        self._xml_parse_complete = True
        log.info(f"No more conversations to process")

        return
