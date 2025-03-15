from bbg_helpers.es_bbg_ib_index import BBG_IB, bloomberg_id
from bbg_src.ib_upload_lambda.bbg_ib_conversation.process_single_conversation import (
    msgToGroup,
)
from bbg_src.ib_upload_lambda.bbg_ib_conversation.process_single_conversation_message import (
    ProcessSingleMessage,
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
    '<Message InteractionType="H" DeviceType="M">'
    "<User>"
    "<LoginName>BJNIXON</LoginName>"
    "<FirstName>BEN</FirstName>"
    "<LastName>NIXON</LastName>"
    "<CompanyName>JEFFERIES INTERNATIO</CompanyName>"
    "<EmailAddress>BJNIXON@Bloomberg.net</EmailAddress>"
    "<CorporateEmailAddress></CorporateEmailAddress>"
    "</User>"
    "<DateTime>03/12/2020 20:06:14</DateTime>"
    "<DateTimeUTC>1584043574</DateTimeUTC>"
    "<Content>*** JEFFERIES INTERNATIO (30436661) Disclaimer: Jefferies archives and monitors outgoing and incoming messages. The contents of this message, including any attachments, are confidential to the ordinary user of the address to which it was addressed. If you are not the addressee of this message you may not copy, forward, disclose or otherwise use it or any part of it in any form whatsoever. This message may be produced at the request of regulators or in connection with civil litigation. Jefferies accepts no liability for any errors or omissions arising as a result of transmission. Use by other than intended recipients is prohibited; if you received this transmission in error please contact the sender.</Content>"
    "<ConversationID>PCHAT-0x10000027F01C9</ConversationID>"
    "</Message>"
)


class TestFunctions:
    def test_create_es_bbg_ib_from_xml(self):
        user_list = msgToGroup()
        user_list.add_user(user)
        process_message_obj = ProcessSingleMessage(messageXML=messagexml, messageUsers=user_list)
        response: BBG_IB = process_message_obj._create_es_BBG_IB_from_XML(
            messageXML=messagexml, messageUsers=user_list, roomID="PCHAT-0x10000027F01C9"
        )
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


class TestBugs:
    def test_kirkoswold_many_attachments(self):
        bug_xml = ET.fromstring(
            """  <Message InteractionType="N">
          <User>
            <LoginName>lmcdonald30</LoginName>
            <FirstName>LARRY</FirstName>
            <LastName>MCDONALD</LastName>
            <CompanyName>BEAR TRAPS REPORT LLC, THE</CompanyName>
            <EmailAddress>lmcdonald30@bloomberg.net</EmailAddress>
            <CorporateEmailAddress></CorporateEmailAddress>
          </User>
          <DateTime>07/13/2021 19:08:42</DateTime>
          <DateTimeUTC>1626203322</DateTimeUTC>
          <Content>&quot;The biggest driver has been a “supply chain “ disruption.  Supply could not keep up with DIY demand and then the builders/contractors were shorted. Today, DIY is off 30% making supply available to the distribution networks. But buyers have stayed on the sidelines long enough to see prices around $650. The floor is near and I think lumber supply will be well subscribed as buyers step in. Market demand continues to be fairly strong.&quot;</Content>
          <ConversationID>PCHAT-0x10000028B74F5</ConversationID>
        </Message>"""
        )

        user_list = msgToGroup()
        user_list.add_user(user)
        user_list.add_user(user_1)
        user_list.add_user(user_2)

        process_message_obj = ProcessSingleMessage(messageXML=bug_xml, messageUsers=user_list)
        response: BBG_IB = process_message_obj.process_message()
        assert response.conversationid == "PCHAT-0x10000028B74F5"
