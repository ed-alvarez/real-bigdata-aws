from bbg_helpers.es_bbg_ib_index import BBG_IB, bloomberg_id
from bbg_src.ib_upload_lambda.bbg_ib_conversation.process_single_conversation_message import (
    ProcessSingleMessage,
    msgToGroup,
)
from lxml import etree as ET

user = bloomberg_id()
user.loginname = "BJNIXON"
user.firstname = "BEN"
user.lastname = "NIXON"
user.companyname = "JEFFERIES INTERNATIO"
user.emailaddress = "BJNIXON@Bloomberg.net"
user.domain = "bloomberg.net"

user_1 = bloomberg_id()
user_1.loginname = "LUDOCOHEN"
user_1.firstname = "LUDOVIC"
user_1.lastname = "COHEN"
user_1.companyname = "JEFFERIES INTERNATIO"
user_1.emailaddress = "LUDOCOHEN@Bloomberg.net"
user_1.domain = "bloomberg.net"

user_2 = bloomberg_id()
user_2.loginname = "SEANSYSTEM2"
user_2.firstname = "SEAN"
user_2.lastname = "OLDFIELD"
user_2.uuid = "25813826"
user_2.firmnumber = "848135"
user_2.accountnumber = "30413594"
user_2.companyname = "MIRABELLA FINANCIAL"
user_2.emailaddress = "SEANSYSTEM2@Bloomberg.net"
user_2.corporateemailaddress = "sean@system2capital.com"
user_2.domain = "system2capital.com"

messagexml = ET.fromstring(
    '<Message InteractionType="N" DeviceType="M">'
    "<User>"
    "<LoginName>tfluckiger</LoginName>"
    "<FirstName>THOMAS</FirstName>"
    "<LastName>FLUCKIGER</LastName>"
    "<CompanyName>BRIDPORT &amp; CIE SA</CompanyName>"
    "<EmailAddress>tfluckiger@bloomberg.net</EmailAddress>"
    "<CorporateEmailAddress></CorporateEmailAddress>"
    "</User>"
    "<DateTime>03/01/2021 20:36:48</DateTime>"
    "<DateTimeUTC>1614631008</DateTimeUTC>"
    "<Content>[Bloomberg created note: Remains as a participant of the room.]</Content>"
    "<ConversationID>PCHAT-0x100000282B7CA</ConversationID>"
    "</Message>"
)


class TestFunctions:
    def test_create_es_bbg_ib_from_xml(self):
        user_list = msgToGroup()
        user_list.add_user(user)
        process_message_obj = ProcessSingleMessage(messageXML=messagexml, messageUsers=user_list)
        response: BBG_IB = process_message_obj._create_es_BBG_IB_from_XML(messageXML=messagexml, messageUsers=user_list)
        assert isinstance(response, BBG_IB)
        assert response.conversationid == "PCHAT-0x10000027F01C9"
        assert isinstance(response.from_detail, bloomberg_id)
        assert response.from_ == "BEN NIXON <BJNIXON@Bloomberg.net>"

    def test_process_message(self):
        user_list = msgToGroup()
        user_list.add_user(user)
        user_list.add_user(user_1)
        user_list.add_user(user_2)

        process_message_obj = ProcessSingleMessage(messageXML=messagexml, messageUsers=user_list)
        response: BBG_IB = process_message_obj.process_message()
        assert isinstance(response, BBG_IB)
        assert response.conversationid == "PCHAT-0x10000027F01C9"
        assert isinstance(response.from_detail, bloomberg_id)
        assert response.from_ == "BEN NIXON <BJNIXON@Bloomberg.net>"
        assert user_1 in response.to_detail
        assert user_2 in response.to_detail
        assert user not in response.to_detail
