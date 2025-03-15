from typing import Dict

from bbg_helpers.es_bbg_msg_index import bloomberg_id
from bbg_src.msg_upload_lambda.bbg_message.message_helper import (
    _choose_email_address,
    flaten_address,
    xml_to_dict,
)
from lxml import etree as ET

user_2: bloomberg_id = bloomberg_id()
user_2.loginname = "SEANSYSTEM2"
user_2.firstname = "SEAN"
user_2.lastname = "OLDFIELD"
user_2.bloomberguuid = "25813826"
user_2.firmnumber = "848135"
user_2.accountnumber = "30413594"
user_2.accountname = "MIRABELLA FINANCIAL"
user_2.bloombergemailaddress = "SEANSYSTEM2@Bloomberg.net"
user_2.corporateemailaddress = "sean@system2capital.com"
user_2.domain = "system2capital.com"


class TestFunctions:
    def test_xml_to_dict_no_attachment(self):
        testAttachment_1_XML: ET = ET.fromstring(
            "<Attachment><Reference>RUNZ READONLY 5E6BDF4600022A712929B39A</Reference></Attachment>"
        )
        response: Dict = xml_to_dict(itemXML=testAttachment_1_XML)
        assert response["reference"] == "RUNZ READONLY 5E6BDF4600022A712929B39A"

    def test_xml_to_dict_actual_attachment(self):
        testAttachment_2_XML: ET = ET.fromstring(
            "<Attachment><FileName>20200314.Mkt_Cap_EUR50M_DevEur.csv</FileName><FileID>5E6C4FF600007A3007F534C6.csv</FileID><FileSize>4037</FileSize></Attachment>"
        )
        response: Dict = xml_to_dict(itemXML=testAttachment_2_XML)
        assert response["filename"] == "20200314.Mkt_Cap_EUR50M_DevEur.csv"

    def test_choose_email_address(self):
        response: str = _choose_email_address(contact=user_2)
        assert response == "sean@system2capital.com"

    def test_flaten_address(self):
        response: str = flaten_address(address=user_2)
        assert response == "SEAN OLDFIELD <sean@system2capital.com>"
