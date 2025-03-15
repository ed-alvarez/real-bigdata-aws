import os
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


class TestFunctions:
    tarFileName = f"{BASE_DIR}/fixtures/new_bbg/f908067.ib19.att.210302.tar.gz"
    tar_file_contents = open(tarFileName, "rb").read()

    conversation_XML = ET.parse(f"{BASE_DIR}/fixtures/new_bbg/single_conversation_1.xml")

    conversation_XML_root = conversation_XML.getroot()

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
            Attachments_FileName=TestFunctions.tarFileName,
            Attachments_FileContent=TestFunctions.tar_file_contents,
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
            Attachments_FileName=TestFunctions.tarFileName,
            Attachments_FileContent=TestFunctions.tar_file_contents,
        )

        result = conversation_obj._has_es_limit_been_reached(**input)
        assert result is expected

    def test_sucessful_completion(self, test_lambda_context):

        conversation_obj = ProcessConversation(
            conversationXML=TestFunctions.conversation_XML_root,
            awsLambdaContext=test_lambda_context,
            fingerprintMeta=FingerprintHelper(),
            Attachments_FileName=TestFunctions.tarFileName,
            Attachments_FileContent=TestFunctions.tar_file_contents,
        )

        response = conversation_obj.process_conversation()
        assert conversation_obj.conversationProccessingComplete == True


class TestBugs:
    tarFileName = f"{BASE_DIR}/bugs/f886973.ib19.att.210713.tar.gz"
    tar_file_contents = open(tarFileName, "rb").read()

    conversation_XML = ET.parse(f"{BASE_DIR}/bugs/19_bad_conversation_kirkoswald_210713.xml")

    conversation_XML_root = conversation_XML.getroot()

    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_kirkoswold_many_attachments(self, test_lambda_context):
        with patch.object(process_single_conversation, "IB_UPLOAD_TO_ES", False):
            conversation_obj = ProcessConversation(
                conversationXML=TestBugs.conversation_XML_root,
                awsLambdaContext=test_lambda_context,
                fingerprintMeta=FingerprintHelper(),
                Attachments_FileName=TestBugs.tarFileName,
                Attachments_FileContent=TestBugs.tar_file_contents,
            )

            response = conversation_obj.process_conversation()
            assert conversation_obj.conversationProccessingComplete == True
