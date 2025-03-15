"""Settings for the module"""
import os

from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.environ.get("LOGGING_LEVEL", "INFO")
BOTO_LOG_LEVEL = os.environ.get("BOTO_LOGGING_LEVEL", "INFO")
STAGE = os.environ.get("STAGE", "dev")

ES_CONNECTION = {}
ES_CONNECTION["hosts"] = os.getenv("ES_HOST")
ES_CONNECTION["http_auth"] = (os.getenv("ES_USER"), os.getenv("ES_PASSWORD"))
ES_CONNECTION["scheme"] = "https"
ES_CONNECTION["timeout"] = 60
ES_CONNECTION["port"] = 9243
ES_CONNECTION["verify_certs"] = True

ES_OP_TYPE = "index"  # Use index to update record if found

DYNAMO_DB = os.environ.get("DYNAMO_DB", False)
MOVE_FILES = os.environ.get("MOVE_FILES", True)
UPLOAD_TO_ES = os.environ.get("UPLOAD_TO_ES", True)
INPUT_INDEX = os.environ.get("ES_INDEX", "ips_data_input_whatsapp")

DYNAMO_DB_TABLE = os.environ.get("DYNAMO_DB_TABLE", "dev_inbound_email")

S3_BUCKET_TODO = "todo.whatsapp"
S3_BUCKET_PROCESSED = "processed.whatsapp"
S3_BUCKET_ARCHIVED = "archive.whatsapp"

MSG_TYPE = "whatsapp"

GRAPHICS_FILE_EXTENSIONS = ["gif", "png", "bmp", "jpg"]
HTML_TAGS_BLACKLIST = [
    "[document]",
    "noscript",
    "header",
    "html",
    "meta",
    "head",
    "input",
    "script",
    "style",
    "xml"
    # there may be more elements you don't want, such as "style", etc.
]

WHATSAPP_KEYS = [
    "X-TELEMESSAGE-ArchiveInitiator",
    "X-TELEMESSAGE-THREAD_ID",
    "X-TELEMESSAGE-OriginalMesageIntegrity",
    "X-TELEMESSAGE-Network",
    "X-TELEMESSAGE-ThreadName",
    "X-TELEMESSAGE-ArchiveMessageID",
    "X-TELEMESSAGE-MessageType:",
    "X-TELEMESSAGE-ArchiveSource",
    "X-TELEMESSAGE-SID",
    "X-TELEMESSAGE-GroupID",
    "X-TELEMESSAGE-GROUP_NAME",
    "X-TELEMESSAGE-Status",
    "Return-Path",
    "RCPT_TO",
    "Content-Transfer-Encoding",
]

MIME_KEYS = ["Date", "To", "From", "Subject", "Sender", "Thread-Index", "body", "attachments"]
