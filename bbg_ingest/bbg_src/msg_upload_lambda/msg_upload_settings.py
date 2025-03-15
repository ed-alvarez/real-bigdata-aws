import os
from enum import Enum

from bbg_helpers.es_bbg_msg_index import DataInput as MSG_DataInput
from bbg_helpers.es_bbg_msg_index import Schema as MSG_Schema


# Top Level BBG XML Items that need some form of processing
class XMLitem(Enum):
    type = "Type"
    user = "User"
    message = "Message"
    attachment = "Attachment"
    sender = "Sender"
    recipient = "Recipient"
    origsender = "OrigSender"
    filename = "FileName"
    fileid = "FileID"
    filesize = "filesize"


# Attributes of top level XML Items
class XMLAttrib(Enum):
    deliverytype = "DeliveryType"


# ES Fields for matching
class ESField(Enum):
    attachment = "attachment"
    attachments = "attachments"
    m_from = "from"
    m_o_from = "from_orig"
    to = "to"
    id = "es_id"
    fileB64content = "fileB64content"
    user = "user"
    msgid = "msgid"
    fileID = "fileid"
    datetime = "msgtime"
    datetimeutc = "msgdatetimeutc"
    AttachmentError = "error"


MSG_GRAPHICS_FILE_EXTENSIONS = [".gif", ".png", ".bmp", ".jpg"]
MSG_AWS_TIMEOUT_MILLISECONDS = int(os.environ.get("MSG_AWS_TIMEOUT_MILLISECONDS", 60000))
MSG_EMAIL_BATCH_SIZE = int(os.environ.get("MSG_BATCH_SIZE", 500))
MSG_EMAIL_LIST_SIZE = int(os.environ.get("MSG_LIST_SIZE", 5000000))
MSG_ES_BULK = os.environ.get("MSG_ES_BULK", True)  # True
MSG_ES_INDEX = os.environ.get("ES_INDEX", "test-v2-bbg-parse-msg")
MSG_ES_PIPELINE = os.environ.get("ES_PIPELINE", "bbg-msg-parse")
MSG_ES_Schema = MSG_Schema.version
MSG_ES_INPUT_ALIAS = MSG_DataInput.alias
