from pathlib import Path

import pytest
from bbg_helpers.es_bbg_ib_index import BBG_IB, bloomberg_id
from bbg_helpers.helper_fingerprint import FingerprintHelper
from bbg_src.ib_upload_lambda.bbg_ib_conversation import process_single_conversation
from bbg_src.ib_upload_lambda.bbg_ib_conversation.process_single_conversation import (
    ProcessConversation,
)
from lxml import etree as ET
from mock import patch

user_0 = bloomberg_id()
user_0.loginname = "BJNIXON"
user_0.firstname = "BEN"
user_0.lastname = "NIXON"
user_0.companyname = "JEFFERIES INTERNATIO"
user_0.emailaddress = "BJNIXON@Bloomberg.net"
user_0.domain = "bloomberg.net"

user_1 = bloomberg_id()
user_1.loginname = "LUDOCOHEN"
user_1.firstname = "LUDOVIC"
user_1.lastname = "COHEN"
user_1.companyname = "JEFFERIES INTERNATIO"
user_1.emailaddress = "LUDOCOHEN@Bloomberg.net"
user_1.domain = "bloomberg.net"

item_BBG_IB_same_to_as_from: BBG_IB = BBG_IB()
item_BBG_IB_same_to_as_from.to_detail = [user_1]
item_BBG_IB_same_to_as_from.from_detail = user_1

item_BBG_IB_different_to_as_from: BBG_IB = BBG_IB()
item_BBG_IB_different_to_as_from.to_detail = [user_0]
item_BBG_IB_different_to_as_from.from_detail = user_1

item_BBG_IB_no_to: BBG_IB = BBG_IB()
item_BBG_IB_no_to.from_detail = user_1

BASE_DIR = Path(__file__).resolve().parent.parent

tarFileName = f"{BASE_DIR}/fixtures/2020-03-16/decoded/f848135.att.200316.tar.gz"
tar_file_contents = open(tarFileName, "rb").read()

conversation_XML = ET.parse(f"{BASE_DIR}/fixtures/bbg_ib/single_conversation_f848135.ib.200316.xml")
conversation_XML_root = conversation_XML.getroot()


class TestFunctions:
    def test_is_message_from_and_to_the_same_user(self, test_lambda_context):
        CASES = [
            (item_BBG_IB_same_to_as_from, True),
            (item_BBG_IB_different_to_as_from, False),
            (item_BBG_IB_no_to, False),
        ]

        blank_conversation_xml = ET.Element("root")
        conversation_obj = ProcessConversation(
            conversationXML=blank_conversation_xml,
            awsLambdaContext=test_lambda_context,
            fingerprintMeta=FingerprintHelper(),
            Attachments_FileName=tarFileName,
            Attachments_FileContent=tar_file_contents,
        )

        for input, expected in CASES:
            result = conversation_obj._is_message_from_and_to_the_same_user(message_detail=input)
            assert result is expected

    batch_too_many_items = {"message_id": 5001, "message_list_size": 0}
    batch_too_large = {"message_id": 0, "message_list_size": 20000001}
    loop_again = {"message_id": 0, "message_list_size": 0}

    CASES = [(batch_too_many_items, True), (batch_too_large, True), (loop_again, False)]

    @pytest.mark.parametrize("input,expected", CASES)
    def test_has_loop_limit_been_reached(self, test_lambda_context, input, expected):

        blank_conversation_xml = ET.Element("root")
        conversation_obj = ProcessConversation(
            conversationXML=blank_conversation_xml,
            awsLambdaContext=test_lambda_context,
            fingerprintMeta=FingerprintHelper(),
            Attachments_FileName=tarFileName,
            Attachments_FileContent=tar_file_contents,
        )

        result = conversation_obj._has_es_limit_been_reached(**input)
        assert result is expected

    def test_sucessful_completion(self, test_lambda_context):
        with patch.object(process_single_conversation, "IB_UPLOAD_TO_ES", False):
            conversation_XML_root = conversation_XML.getroot()
            conversation_obj = ProcessConversation(
                conversationXML=conversation_XML_root,
                awsLambdaContext=test_lambda_context,
                fingerprintMeta=FingerprintHelper(),
                Attachments_FileName=tarFileName,
                Attachments_FileContent=tar_file_contents,
            )

            response = conversation_obj.process_conversation()
            assert conversation_obj.conversationProccessingComplete == True
