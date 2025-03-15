"""
Helper functions for bloomberg_id creation
"""

import logging
from typing import List

from bbg_helpers.es_bbg_ib_index import bloomberg_id
from bbg_src.ib_upload_lambda.ib_upload_settings import XMLitem
from lxml import etree as ET

log = logging.getLogger()


def _get_domain(email_address: str) -> str:
    if email_address:
        return email_address.split("@")[-1].lower()


# Iterate an XML User object and turn keys to lower case for ES
# Expected children could be: LoginName FirstName LastName ClientID1 ClientID2 UUID
# FirmNumber AccountNumber CompanyName EmailAddress CorporateEmailAddress
def create_es_bloomberg_id_from_xml_item(userXML: ET) -> bloomberg_id:
    user: bloomberg_id = bloomberg_id()
    item: ET
    for item in userXML:
        if item.text:
            setattr(user, item.tag.lower(), item.text)
    if "corporateemailaddress" in user:
        user.domain = _get_domain(user.corporateemailaddress)
    else:
        user.domain = _get_domain(user.emailaddress)
    return user


# Process Participant XML and return a User
def xml_to_es_bloomberg_id(participantXML: ET) -> bloomberg_id:
    participant_user: bloomberg_id = bloomberg_id()

    participant: ET
    for participant in participantXML:
        if participant.tag == XMLitem.user.value:
            participant_user = create_es_bloomberg_id_from_xml_item(userXML=participant)

    return participant_user


def _choose_email_address(contact: bloomberg_id) -> str:
    if "corporateemailaddress" in contact:
        return contact.corporateemailaddress
    else:
        return contact.emailaddress


def flaten_address(address: bloomberg_id) -> str:
    flat_address: str = str()
    email: str = _choose_email_address(address)
    flat_address = f"{address.firstname} {address.lastname} <{email}>"
    return flat_address


def flaten_list_of_addresses(address_list: List[bloomberg_id]) -> List[str]:
    flat_address_list: List[str] = []
    sender: bloomberg_id
    for sender in address_list:
        email: str = _choose_email_address(sender)
        address: str = f"{sender.firstname} {sender.lastname} <{email}>"
        flat_address_list.append(address)
    return flat_address_list
