import os
from enum import Enum

from bbg_helpers.es_bbg_ib_index import DataInput as IB_DataInput
from bbg_helpers.es_bbg_ib_index import Schema as IB_Schema


# Top level BBG XML Items that need some form of processing
class XMLitem(Enum):
    user = "User"
    attachment = "Attachment"
    conversation = "Conversation"
    message = "Message"
    participantentered = "ParticipantEntered"
    participantleft = "ParticipantLeft"
    filename = "FileName"
    fileid = "FileID"
    filesize = "filesize"
    roomID = "RoomID"


# Attributes of top level XML items
class XMLattr(Enum):
    roomtype = "RoomType"


# ES fields for matching
class ESField(Enum):
    to = "to"
    m_from = "from"
    attachments = "attachments"
    attachment = "attachment"
    id = "es_id"
    fileB64content = "fileB64content"
    conversationid = "conversationid"
    fileID = "fileid"
    datetime = "datetime"
    datetimeutc = "datetimeutc"
    AttachmentError = "error"
    user = "user"
    item_id = "item_id"


IB_AWS_TIMEOUT_MILLISECONDS = int(os.environ.get("IB_AWS_TIMEOUT_MILLISECONDS", 60000))
IB_MESSAGE_BATCH_SIZE = int(os.environ.get("IB_MESSAGE_BATCH_SIZE", 5000))
IB_MESSAGE_LIST_SIZE = int(os.environ.get("IB_MESSAGE_LIST_SIZE", 20000000))

IB_ES_INPUT_ALIAS = IB_DataInput.alias
IB_ES_SCHEMA = IB_Schema.version
IB_ES_PIPELEINE = os.environ.get("IB_ES_PIPELINE", "bbg-ib-parse")
IB_UPLOAD_TO_ES = os.environ.get("IB_UPLOAD_TO_ES", True)  # True
IB_ES_INDEX = os.environ.get("ES_INDEX", "test-v2-bbg-parse-ib")

IB_GRAPHICS_FILE_EXTENSIONS = [".gif", ".png", ".bmp", ".jpg"]
