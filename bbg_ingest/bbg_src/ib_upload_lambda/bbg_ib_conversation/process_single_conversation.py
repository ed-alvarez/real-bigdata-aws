"""
- Each bbg_ib_conversation is parsed for
    - Participant Entering
    - Participant Leaving
    - Sending an Attachment

    - Sending a Message
- The audience of the Message or the Attachment is important:
    - A list of all bbg_ib_conversation participants at any time is kept for each bbg_ib_conversation and generated from the
    Participant Enters and Participant leaves
    - Each attachment and message has a FROM.  The to is generated from the participants list MINUS the FROM.
    This demonstrates who would have been able to receive the message or attachment.

- Once a bbg_ib_conversation has been iterated for all items the relevant fingerprint meta data is inserted
"""
import logging
from typing import List

from aws_lambda_context import LambdaContext
from bbg_helpers.es_bbg_ib_index import BBG_IB, bloomberg_id
from bbg_helpers.es_bulk import IB_esBulk
from bbg_helpers.helper_fingerprint import FingerprintHelper
from bbg_src.ib_upload_lambda.bbg_ib_conversation.address_group import msgToGroup
from bbg_src.ib_upload_lambda.bbg_ib_conversation.conversation_bulk_object import (
    ibConversation,
)
from bbg_src.ib_upload_lambda.bbg_ib_conversation.es_bloomberg_id_helper import (
    xml_to_es_bloomberg_id,
)
from bbg_src.ib_upload_lambda.bbg_ib_conversation.es_item_id_helper import (
    generate_item_id,
)
from bbg_src.ib_upload_lambda.bbg_ib_conversation.process_single_conversation_attachment import (
    ProcessSingleAttachment,
)
from bbg_src.ib_upload_lambda.bbg_ib_conversation.process_single_conversation_message import (
    ProcessSingleMessage,
)
from bbg_src.ib_upload_lambda.ib_upload_settings import (
    IB_ES_INPUT_ALIAS,
    IB_ES_PIPELEINE,
    IB_MESSAGE_BATCH_SIZE,
    IB_MESSAGE_LIST_SIZE,
    IB_UPLOAD_TO_ES,
    XMLitem,
)
from elasticsearch import exceptions
from lxml import etree as ET

from shared.shared_src.utils import human_readable_size, timing

log = logging.getLogger()


# Iterate over an Individual Conversation Item
# This holds all the bbg_ib_conversation items Join, Leave, message & attachment
# The Child items can be: RoomID StartTime StartTimeUTC Attachment Invite
# ParticipantEntered ParticipantLeft Message History SystemMessage EndTime EndTimeUTC


class ProcessConversation:
    def __init__(
        self,
        conversationXML: ET,
        awsLambdaContext: LambdaContext,
        fingerprintMeta: FingerprintHelper,
        Attachments_FileName: str = "",
        Attachments_FileContent: bytes = None,
    ) -> None:
        self._conversationXML: ET = conversationXML
        self._tar_FileName: str = Attachments_FileName
        self._tar_FileContents: bytes = Attachments_FileContent
        self._fingerprint_meta: FingerprintHelper = fingerprintMeta
        self._aws_context: LambdaContext = awsLambdaContext
        self._next_item: int = 0

        self._es_index = IB_ES_INPUT_ALIAS
        self._es_pipeline = IB_ES_PIPELEINE
        self._es_bulk: IB_esBulk = IB_esBulk()

        self._conversation_processing_completed: bool = False

    @property
    def conversationProccessingComplete(self):
        return self._conversation_processing_completed

    def _is_message_from_and_to_the_same_user(self, message_detail: BBG_IB) -> bool:
        state = False
        if message_detail.to_detail:
            if len(message_detail.to_detail) == 1 and (message_detail.to_detail[0] == message_detail.from_detail):
                state = True
        return state

    def _has_es_limit_been_reached(self, message_id: int, message_list_size: int) -> bool:
        if message_id >= IB_MESSAGE_BATCH_SIZE:
            log.info(f"ES Limit: BATCH SIZE {message_id} is greater or equal to {IB_MESSAGE_BATCH_SIZE}")
            return True
        elif message_list_size >= IB_MESSAGE_LIST_SIZE:
            log.info(f"ES Limit: ES UPLOAD SIZE {message_list_size} is greater or equal to {IB_MESSAGE_LIST_SIZE}")
            return True
        else:
            return False

    def _upload_to_es(self, items_to_upload: List):
        log.debug("Interim Upload bbg_ib_conversation to ElasticSearch")
        self._es_bulk.esBulkData = items_to_upload
        self._es_bulk.convert_data_to_es_bulk()
        try:
            self._es_bulk.upload_data()
            log.debug("Conversation sucessfully Uploaded to ElasticSearch")
        except exceptions.ElasticsearchException as ex:
            log.exception(ex)
            log.error("Error Uploading Conversation to ElasticSearch")
            raise ex
        return

    @timing
    def process_conversation(self) -> ibConversation:
        log.debug("Process a Conversation")
        message_users: msgToGroup = msgToGroup()
        conversation_items: ibConversation = ibConversation()
        message_id = 0
        items = len(list(self._conversationXML))

        room_id = getattr(self._conversationXML.find("RoomID"), "text", "Missing Room ID")
        room_start_time = getattr(self._conversationXML.find("StartTime"), "text", "Missing Start Time")
        room_end_time = getattr(self._conversationXML.find("EndTime"), "text", "Missing End Time")
        messages_to_process = len(self._conversationXML.findall("Message"))
        attachments_to_process = len(self._conversationXML.findall("Attachment"))
        log.info(f"Room {room_id}, Message_Items : {messages_to_process}, Attachments : {attachments_to_process}")

        if IB_UPLOAD_TO_ES:
            self._es_bulk.esIndex = self._es_index
            self._es_bulk.esPipeline = self._es_pipeline
            self._es_bulk.set_parameters()

        loop: int
        xml_item: ET
        for loop, xml_item in enumerate(self._conversationXML):

            # the start_at_item is always one ahead of the loop processed so that if the loop times out the correct start_at
            # value is passed to the  output data class for the next iteration
            self._next_item = loop + 1

            log.debug(f"Process bbg_ib_conversation item {loop}")

            # TODO Process invites

            # Process an attachment
            if xml_item.tag == XMLitem.attachment.value:
                log.debug(f"Conversation Item {loop} is an Attachment")
                this_attachment_obj: ProcessSingleAttachment = ProcessSingleAttachment(
                    attachmentXML=xml_item,
                    attachmentUsers=message_users,
                    Attachments_FileName=self._tar_FileName,
                    Attachments_FileContent=self._tar_FileContents,
                )
                attachment_details: BBG_IB = this_attachment_obj.process_attachment()
                attachment_details.item_id = generate_item_id(ibMessage=attachment_details, messageNumber=message_id)
                message_id += 1
                self._fingerprint_meta.set_msg_time(msg_time=attachment_details.datetime)
                attachment_details.fingerprint = self._fingerprint_meta.fingerprint_meta_data
                conversation_items.add_ib(attachment_details)
                del attachment_details
                del this_attachment_obj

            # Process a Message
            if xml_item.tag == XMLitem.message.value:
                log.debug(f"Conversation Item {loop} is a Message")

                # Next item if Bloomberg Generated  or a history item
                content = getattr(xml_item.find("Content"), "text", "")
                matches = ["[Bloomberg created note:", "BACKFILL CONTENT AUTOGENERATED FROM HISTORY"]
                if any(x in content for x in matches):
                    continue

                this_message_obj: ProcessSingleMessage = ProcessSingleMessage(
                    messageXML=xml_item, messageUsers=message_users, roomID=room_id
                )
                message_details: BBG_IB = this_message_obj.process_message()

                try:
                    # This is here due to the kirkoswold many attachments bug
                    message_details.conversationid = room_id
                    message_details.item_id = generate_item_id(ibMessage=message_details, messageNumber=message_id)
                except Exception as ex:
                    raise ex
                message_id += 1
                # Update Fingerprint metadata with item date
                self._fingerprint_meta.set_msg_time(msg_time=message_details.datetime)
                message_details.fingerprint = self._fingerprint_meta.fingerprint_meta_data

                # Remove messages that seem to be start of day initialisation
                # to = 1 user and it's the same user as the message is from
                if self._is_message_from_and_to_the_same_user(message_detail=message_details):
                    continue
                conversation_items.add_ib(message_details)

                # remove message details object
                del message_details
                del this_message_obj

            # Process Participant Entered by adding the user to the Participants list
            if xml_item.tag == XMLitem.participantentered.value:
                log.debug(f"Conversation Item {loop} is Participant Entered")
                participant_entered: bloomberg_id = xml_to_es_bloomberg_id(participantXML=xml_item)
                message_users.add_user(participant_entered)

            # Process Participant Left by removing the user from the Participants List
            if xml_item.tag == XMLitem.participantleft.value:
                log.debug(f"Conversation Item {loop} is Participant Left")
                participant_left: bloomberg_id = xml_to_es_bloomberg_id(participantXML=xml_item)
                message_users.remove_user(participant_left)

            # Check if an ES limit has been reached
            # Limit number of items or size of data
            if self._has_es_limit_been_reached(message_id=message_id, message_list_size=conversation_items.ibListSize):

                # Upload interim parts of a bbg_ib_conversation to ES
                es_num_items: int = len(conversation_items.listOfIBItems)
                es_upload_size: str = human_readable_size(size=conversation_items.ibListSize)
                log.info(f"Uploading to ES {es_num_items} items, with size of {es_upload_size}")
                if IB_UPLOAD_TO_ES:
                    self._upload_to_es(conversation_items.listOfIBItems)
                    # Replace ES storage loop
                del conversation_items
                conversation_items: ibConversation = ibConversation()

        # if we have got here then the bbg_ib_conversation processing has completed
        # This will return with the ConversationProccessingComplete remaining as False
        self._conversation_processing_completed = True

        es_num_items: int = len(conversation_items.listOfIBItems)
        es_upload_size: str = human_readable_size(size=conversation_items.ibListSize)
        log.info(f"Uploading to ES {es_num_items} items, with size of {es_upload_size}")
        if IB_UPLOAD_TO_ES:
            self._upload_to_es(conversation_items.listOfIBItems)
        return conversation_items
