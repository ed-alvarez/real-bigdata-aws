"""
- Message processing
    = The content is extracted from the XML
    - The ES ID is generated from the Conversation name, Conversation Date plus the iteration number of Attachments
      and Messages
    - The From is extracted from the XML
    - The To is generated from the Participant list
    - The date/time is captured from the XML
"""

import logging

from bbg_helpers.es_bbg_ib_index import BBG_IB, bloomberg_id
from bbg_src.ib_upload_lambda.bbg_ib_conversation.address_group import msgToGroup
from bbg_src.ib_upload_lambda.bbg_ib_conversation.es_bloomberg_id_helper import (
    create_es_bloomberg_id_from_xml_item,
    flaten_address,
    flaten_list_of_addresses,
)
from bbg_src.ib_upload_lambda.ib_upload_settings import XMLitem
from lxml import etree as ET

log = logging.getLogger()


def de_html_ify(text):
    """Replace <, >, &, " with their HTML encoded representation. Intended to
    prevent HTML errors in rendered displaCy markup.
    text (unicode): The original text.
    RETURNS (unicode): Equivalent text to be safely used within HTML.
    """
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    return text


# Process the Message XML
class ProcessSingleMessage:
    def __init__(self, messageXML: ET, messageUsers: msgToGroup, roomID: str = ""):
        self._messageXML: ET = messageXML
        self._messageUsers: msgToGroup = messageUsers
        self._room_id: str = roomID

        # Iterate an XML Message object and turn keys to lower case for ES
        # Expected children could be: User DateTime DateTimeUTC Content ConversationID, from_

    def _create_es_BBG_IB_from_XML(self, messageXML: ET, messageUsers: msgToGroup, roomID: str) -> BBG_IB:
        message = BBG_IB()

        item: ET
        for item in self._messageXML:
            if item.tag.lower() == "conversationid":
                message.conversationid = getattr(item, "text", roomID)

            # Change content -> body
            elif item.tag.lower() == "content":
                message.body = de_html_ify(text=item.text)

            # Populate From User
            elif item.tag == XMLitem.user.value:
                user: bloomberg_id = create_es_bloomberg_id_from_xml_item(userXML=item)
                message.from_detail = user
                message.from_ = flaten_address(user)

            # Populate other bits of schema
            else:
                setattr(message, item.tag.lower(), item.text)

        return message

    def process_message(self) -> BBG_IB:
        message_details: BBG_IB = BBG_IB()
        message_details = self._create_es_BBG_IB_from_XML(
            messageXML=self._messageXML, messageUsers=self._messageUsers, roomID=self._room_id
        )
        message_details.to_detail = self._messageUsers.get_to_list(messageFrom=message_details.from_detail)
        message_details.to = flaten_list_of_addresses(message_details.to_detail)
        return message_details
