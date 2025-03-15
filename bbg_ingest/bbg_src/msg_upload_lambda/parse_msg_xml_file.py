# import xml.etree.ElementTree as ET
# from xml.etree.ElementTree import XMLParser
# from xml.etree.ElementTree import ParseError

import logging
import os
from io import BytesIO
from itertools import islice

from aws_lambda_context import LambdaContext
from bbg_helpers.es_bbg_msg_index import BBG_MSG
from bbg_helpers.es_bulk import MSG_esBulk
from bbg_helpers.helper_file import BBGFileHelper
from bbg_helpers.helper_fingerprint import FingerprintHelper
from bbg_settings import UPLOAD_TO_ES
from bbg_src.msg_upload_lambda.bbg_message.message_bulk_object import (
    msg_bulk_collection,
)
from bbg_src.msg_upload_lambda.bbg_message.process_message import ProcessMessage
from bbg_src.msg_upload_lambda.msg_upload_settings import (
    MSG_AWS_TIMEOUT_MILLISECONDS,
    MSG_EMAIL_BATCH_SIZE,
    MSG_EMAIL_LIST_SIZE,
    MSG_ES_INDEX,
    MSG_ES_PIPELINE,
    MSG_Schema,
    XMLitem,
)
from elasticsearch import exceptions
from lxml import etree as ET
from lxml.etree import ParseError, XMLParser

from shared.shared_src.s3.s3_helper import S3Helper
from shared.shared_src.utils import timing

log = logging.getLogger()
if os.environ.get("AWS_EXECUTION_ENV") is None:
    ch = logging.StreamHandler()
    log.addHandler(ch)


class ParseBBGXMLtoES:
    def __init__(
        self,
        msg_FileContents: bytes,
        msg_FileName: str,
        tar_FileContents: bytes,
        tar_FileName: str,
        awsContext: LambdaContext,
        xmlMessageNumber: int,
        S3_helper: S3Helper,
    ):

        self._msg_FileContents: bytes = msg_FileContents
        self._msg_file_name: str = msg_FileName
        log.debug(f"self._msg_file_name: {self._msg_file_name}")
        self._tar_FileContents: bytes = tar_FileContents
        self._tar_file_name: str = tar_FileName
        log.debug(f"self._tar_file_name: {self._tar_file_name}")
        self._s3_obj: S3Helper = S3_helper
        self._aws_context: LambdaContext = awsContext
        self._xml_iteration_start_item: int = xmlMessageNumber

        self._xml_iteration_next_item: int = 0

        self._bucket_name: str = str()
        self._client_name: str = str()
        self._es_index: str = str()
        self._es_pipeline: str = str()

        self._xml_tree: ET = None
        self._xml_root: ET = None
        self._xml_parse_complete: bool = False
        # Set to false for Step function.  Only set to true when XML has finished processing

        self._fingerprint_meta: FingerprintHelper = FingerprintHelper()

    @property
    def xmlParseComplete(self):
        return self._xml_parse_complete

    @property
    def xmlItemNextStart(self):
        return self._xml_iteration_next_item

    def initialise_variables(self):
        self._bucket_name = self._s3_obj.bucketName
        self._client_name = self._s3_obj.clientName
        self._es_index = MSG_ES_INDEX
        self._es_pipeline = MSG_ES_PIPELINE
        # parser : XMLParser = XMLParser(encoding="utf-8")
        parser: XMLParser = XMLParser(recover=True)
        try:
            self._xml_tree = ET.parse(BytesIO(self._msg_FileContents), parser=parser)

        except ParseError as ex:
            log.exception(ex)
            log.error(f"Cannot open the XML file {self._msg_file_name}: {ex}")
            raise ex
        self._xml_root = self._xml_tree.getroot()
        log.info(f"item in self._xml_root: {len(self._xml_root)}")

        self._fingerprint_meta = FingerprintHelper()
        self._fingerprint_meta.set_client_name(client_name=self._client_name)

        # Set key location to where the file will end up
        file_helper = BBGFileHelper(file=self._msg_file_name)
        self._fingerprint_meta.set_key_name(key_name=file_helper.file_key)
        self._fingerprint_meta.set_bucket_name(bucket_name=self._bucket_name)
        self._fingerprint_meta.set_msg_type(msg_type="bbg.msg")
        self._fingerprint_meta.set_schema(MSG_Schema.version)

    # Work out from the XML if to skip a branch of the XML tree
    # Order is important and works from MOST specific (topic, from etc) to LEAST specific (XML Type)
    # Returns TRUE to skip. Defaults to False
    def _skip_this_node(self, level1XML) -> bool:
        skip_this: bool = False

        # Removes auto generated ALRT messages from BBG
        if level1XML.findall("./Sender/UserInfo/[LastName='ALERT']"):
            skip_this = True
            return skip_this

        # Is the record type a Message (this gets rid of BBG XML file header
        if level1XML.tag != XMLitem.message.value:
            skip_this = True
            return skip_this

        return skip_this

    def _time_for_another_batch(self) -> bool:
        time_remaining: int = self._aws_context.get_remaining_time_in_millis()
        if time_remaining <= MSG_AWS_TIMEOUT_MILLISECONDS:
            log.info(f"{time_remaining / 1000} seconds left. No Time for another loop")
            return False
        else:
            log.info(f"{time_remaining / 1000} seconds left. Time for another loop")
            return True

    def _upload_to_elasticsearch(self, es_bulk: MSG_esBulk, batch_email_data: msg_bulk_collection) -> None:
        es_bulk.esBulkData = batch_email_data.listOfMSGItems
        try:
            es_bulk.convert_data_to_es_bulk()
        except exceptions as ex:
            log.exception(ex)
            raise ex
        try:
            es_bulk.upload_data()
        except exceptions.ElasticsearchException as ex:
            log.exception(ex)
            raise ex
        return

    def _has_loop_limit_been_reached(self, msgListCount: int, msgListSize: int) -> bool:
        if msgListCount >= MSG_EMAIL_BATCH_SIZE:
            log.info(f"Loop Limit: BATCH SIZE {msgListCount} is greater or equal to {MSG_EMAIL_BATCH_SIZE}")
            return True
        elif msgListSize >= MSG_EMAIL_LIST_SIZE:
            log.info(f"Loop Limit: ES UPLOAD SIZE {msgListSize} is greater or equal to {MSG_EMAIL_LIST_SIZE}")
            return True
        else:
            return False

    @timing
    def xml_step(self):

        # Pre loop initialisatoin of variables
        batch_email_data = msg_bulk_collection()

        if UPLOAD_TO_ES:
            es_bulk = MSG_esBulk()
            es_bulk.esIndex = self._es_index
            es_bulk.esPipeline = self._es_pipeline
            es_bulk.set_parameters()

        # Using islice to enable starting the XML parse from a previous finish point.
        # If a lambda runs over it can pass the xml_iteration_item back to the step function
        # the step function can kick off the lambda again with the parsing starting from where it
        # left off
        for loop, level_1 in enumerate(islice(self._xml_root, self._xml_iteration_start_item, None)):
            # log.debug(f'In loop {loop}')
            self._xml_iteration_next_item = self._xml_iteration_start_item + loop + 1
            # log.debug(f'next loop value : {self._xml_iteration_next_item}')

            # test to see if this node should be processed
            if self._skip_this_node(level1XML=level_1):
                continue

            # Process an individual bbg_ib_conversation
            bbg_message_obj: ProcessMessage = ProcessMessage(
                emailXML=level_1,
                fingerprintMeta=self._fingerprint_meta,
                Attachments_FileName=self._tar_file_name,
                Attachments_FileContent=self._tar_FileContents,
            )
            try:
                single_email_full: BBG_MSG = bbg_message_obj.process_email()
            except exceptions as ex:
                log.exception(ex)
                raise ex

            batch_email_data.add_msg(single_email_full)

            if self._has_loop_limit_been_reached(msgListCount=batch_email_data.msgListCount, msgListSize=batch_email_data.msgListSize):
                if UPLOAD_TO_ES:
                    self._upload_to_elasticsearch(es_bulk=es_bulk, batch_email_data=batch_email_data)

                # Check the time left from the lambda context.
                # If there is less than the timeout then stop loop
                if not self._time_for_another_batch():
                    return

                # Set up a new collection object
                del batch_email_data
                batch_email_data = msg_bulk_collection()

            del single_email_full
            del bbg_message_obj
            # End of for loop

        # If True then there is NO more XML to parse.  This value will be tested in the Step function loop
        self._xml_parse_complete = True

        # Finish up with the final emails
        if batch_email_data.msgListCount >= 1:
            if UPLOAD_TO_ES:
                self._upload_to_elasticsearch(es_bulk=es_bulk, batch_email_data=batch_email_data)

        del batch_email_data
        if UPLOAD_TO_ES:
            del es_bulk
        return


if __name__ == "__main__":
    import boto3
    from mock import patch

    from bbg_ingest.bbg_helpers import helper_s3
    from bbg_ingest.bbg_tests import TestLambdaContext

    class test_wrapper:
        @patch.object(boto3, "client")
        def test_IB(self, mock_client, context):
            msg_file_name = "/bbg_tests/bugs/f908067.msg.210202.xml"
            tar_file_name = "/bbg_tests/bugs/f908067.msg.att.210202.tar.gz"

            msg_file_contents = open(msg_file_name, "rb")
            tar_file_contents = open(tarFileName, "rb")

            s3_obj = helper_s3.S3Helper()
            s3_obj.clientName = "test_client_name"

            XML_Data = ParseBBGXMLtoES(
                S3_helper=s3_obj,
                msg_FileName=msg_file_name,
                msg_FileContents=msg_file_contents,
                awsContext=context,
                xmlMessageNumber=0,
                tar_FileName=tar_file_name,
                tar_FileContents=tar_file_contents,
            )

            XML_Data.initialise_variables()

            try:
                XML_Data.xml_step()
            except exceptions.ElasticsearchException as ex:
                log.exception(ex)
                log.error("ElasticSearchGeneralError")

    context = TestLambdaContext(time_limit_in_seconds=9000)
    test = test_wrapper()
    test.test_IB(context=context)
