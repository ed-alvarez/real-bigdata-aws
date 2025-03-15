import xml.etree.ElementTree as ET
from typing import Dict

from bbg_helpers.es_bbg_msg_index import bloomberg_id


def xml_to_dict(itemXML: ET) -> Dict[str, str]:
    item_dict: Dict[str, str] = {}
    item: ET
    for item in itemXML:
        item_dict[item.tag.lower()] = item.text
    return item_dict


def xstr(s) -> str:
    """Function to convert to string and return a blank if the input is None"""
    return "" if s is None else str(s)


def _choose_email_address(contact: bloomberg_id) -> str:

    if getattr(contact, "corporateemailaddress"):
        return contact.corporateemailaddress
    else:
        return contact.bloombergemailaddress


def flaten_address(address: bloomberg_id) -> str:
    flat_address: str = str()
    email: str = _choose_email_address(address)
    flat_address = f"{address.firstname} {address.lastname} <{email}>"
    return flat_address
