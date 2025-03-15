from bbg_helpers.es_bbg_ib_index import bloomberg_id
from bbg_src.ib_upload_lambda.bbg_ib_conversation.es_bloomberg_id_helper import (
    _choose_email_address,
    _get_domain,
    create_es_bloomberg_id_from_xml_item,
    flaten_address,
    flaten_list_of_addresses,
    xml_to_es_bloomberg_id,
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


class TestFunctions:
    def test__get_domain(self):
        CASES = [
            ("james@Hogbin.com", "hogbin.com"),
            ("james@IP-sentinel.com", "ip-sentinel.com"),
            ("james@HOGBIN.COM", "hogbin.com"),
        ]

        for input, expected in CASES:
            result = _get_domain(email_address=input)
            assert result == expected

    def test_create_es_bloomberg_id_from_xml_item_without_corporate_email(self):
        userxml = ET.fromstring(
            """<User>
                                    <LoginName>BJNIXON</LoginName>
                                    <FirstName>BEN</FirstName>
                                    <LastName>NIXON</LastName>
                                    <CompanyName>JEFFERIES INTERNATIO</CompanyName>
                                    <EmailAddress>BJNIXON@Bloomberg.net</EmailAddress>
                                    <CorporateEmailAddress></CorporateEmailAddress>
                                    </User>"""
        )

        response = create_es_bloomberg_id_from_xml_item(userXML=userxml)
        assert isinstance(response, bloomberg_id)
        assert response.loginname == "BJNIXON"
        assert "uuid" not in response
        assert "corporateemailaddress" not in response
        assert response.domain == "bloomberg.net"

    def test_create_es_bloomberg_id_from_xml_item_with_corporate_email(self):
        userxml = ET.fromstring(
            """<User>
                                <LoginName>TARAGS2C</LoginName>
                                <FirstName>TARA</FirstName>
                                <LastName>GIBSON</LastName>
                                <UUID>27186304</UUID>
                                <FirmNumber>848135</FirmNumber>
                                <AccountNumber>30413594</AccountNumber>
                                <CompanyName>MIRABELLA FINANCIAL</CompanyName>
                                <EmailAddress>TARAGS2C@Bloomberg.net</EmailAddress>
                                <CorporateEmailAddress>tara@system2capital.com</CorporateEmailAddress>
                                </User>"""
        )

        response = create_es_bloomberg_id_from_xml_item(userXML=userxml)
        assert isinstance(response, bloomberg_id)
        assert response.loginname == "TARAGS2C"
        assert response.uuid == "27186304"
        assert response.corporateemailaddress == "tara@system2capital.com"
        assert response.domain == "system2capital.com"

    def test_xml_to_es_bloomberg_id_participant_entered(self):
        userxml = ET.fromstring(
            """<ParticipantEntered InteractionType="H" DeviceType="M">
                                <User>
                                <LoginName>BJNIXON</LoginName>
                                <FirstName>BEN</FirstName>
                                <LastName>NIXON</LastName>
                                <CompanyName>JEFFERIES INTERNATIO</CompanyName>
                                <EmailAddress>BJNIXON@Bloomberg.net</EmailAddress>
                                <CorporateEmailAddress></CorporateEmailAddress>
                                </User>
                                <DateTime>03/12/2020 20:06:14</DateTime>
                                <DateTimeUTC>1584043574</DateTimeUTC>
                                <ConversationID>PCHAT-0x10000027F01C9</ConversationID>
                                </ParticipantEntered>"""
        )

        response = xml_to_es_bloomberg_id(participantXML=userxml)
        assert isinstance(response, bloomberg_id)
        assert response.loginname == "BJNIXON"
        assert "uuid" not in response
        assert "corporateemailaddress" not in response

    def test_xml_to_es_bloomberg_id_participant_left(self):
        userxml = ET.fromstring(
            """<ParticipantLeft InteractionType="H">
                                <User>
                                <LoginName>TARAGS2C</LoginName>
                                <FirstName>TARA</FirstName>
                                <LastName>GIBSON</LastName>
                                <UUID>27186304</UUID>
                                <FirmNumber>848135</FirmNumber>
                                <AccountNumber>30413594</AccountNumber>
                                <CompanyName>MIRABELLA FINANCIAL</CompanyName>
                                <EmailAddress>TARAGS2C@Bloomberg.net</EmailAddress>
                                <CorporateEmailAddress>tara@system2capital.com</CorporateEmailAddress>
                                </User>
                                <DateTime>03/13/2020 13:46:23</DateTime>
                                <DateTimeUTC>1584107183</DateTimeUTC>
                                <ConversationID>PCHAT-0x10000027EB748</ConversationID>
                                </ParticipantLeft>"""
        )

        response = xml_to_es_bloomberg_id(participantXML=userxml)
        assert isinstance(response, bloomberg_id)
        assert response.loginname == "TARAGS2C"
        assert response.uuid == "27186304"

    def test__choose_email_address(self):
        CASES = [(user_1, "LUDOCOHEN@Bloomberg.net"), (user_2, "sean@system2capital.com")]

        for input, expected in CASES:
            result = _choose_email_address(input)
            assert result == expected

    def test_flaten_address(self):
        CASES = [
            (user_1, "LUDOVIC COHEN <LUDOCOHEN@Bloomberg.net>"),
            (user_2, "SEAN OLDFIELD <sean@system2capital.com>"),
        ]
        for input, expected in CASES:
            result = flaten_address(input)
            assert result == expected

    def test_flaten_list_of_addresses(self):

        user_list = [user, user_1, user_2]
        expected_result = [
            "BEN NIXON <BJNIXON@Bloomberg.net>",
            "LUDOVIC COHEN <LUDOCOHEN@Bloomberg.net>",
            "SEAN OLDFIELD <sean@system2capital.com>",
        ]

        response = flaten_list_of_addresses(address_list=user_list)
        assert response == expected_result
