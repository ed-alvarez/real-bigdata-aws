"""Settings for the module"""
import os
from distutils import util

from dotenv import load_dotenv

load_dotenv()
from dataclasses import dataclass
from enum import Enum

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

ES_OP_TYPE = "create"  # Use index to update record if found

DYNAMO_DB = os.environ.get("DYNAMO_DB", True)
MOVE_FILES = os.environ.get("MOVE_FILES", True)
ES_UPLOAD = os.environ.get("ES_UPLOAD", True)

DYNAMO_DB_TABLE = os.environ.get("DYNAMO_DB_TABLE", "dev_inbound_email")

S3_BUCKET_TODO = "todo.email"
S3_BUCKET_PROCESSED = "processed.email"
S3_BUCKET_ARCHIVED = "archive.email"

INPUT_INDEX = os.environ.get("ES_INDEX", "ips_data_input_email")

MSG_TYPE = "email"

IGNORE_FILE_EXTENSIONS = ["AdvertisingBranding"]
GRAPHICS_FILE_EXTENSIONS = ["gif", "png", "bmp", "jpg"]
AUDIO_FILE_EXTENSIONS = ["mp3", "mpeg", "wav", "aif"]
ENCRYPTED_FILE_EXTENSIONS = ["pgp"]
COMPRESSED_FILE_EXTENSIONS = ["zip", "tar", "7z", "bz2", "gz" "rar"]
GMAIL_DOMAIN_LIST = ["google.com", "1e100.net"]
EMAIL_SEPARATOR_LIST = [".", "_", "-"]
DONT_PROCESS_EMAIL_SUBJECT_LIST = ["HierarchySync_Ping_", "HierarchySync_IncrementalSync_"]
EMAIL_TO_ADDRESS_NO_DETAIL = [
    "undisclosed",
]
CHARS_TO_NOT_SPLIT_EMAIL_NAME = ["(", ")", "\\", "//"]
ADDRESS_FIELDS = [
    "sender",
    "resent-sender",
    "to",
    "resent-to",
    "cc",
    "resent-cc",
    "bcc",
    "resent-bcc",
    "from",
    "resent-from",
    "reply-to",
]
CONTENT_TYPE_NOT_TO_PROCESS = ["application/octetstream"]
INGEST_TYPE = "email"
SENTIMENT_MAXIMUM_SIZE_TO_ANALYSE = 500000
BODY_PARSER_MAXIMUM_SIZE_TO_ANALYSE = 1000000


@dataclass()
class emailAddress:
    name_part: str = ""
    name_first: str = ""
    name_last: str = ""
    email_part: str = ""
    email_name: str = ""
    email_domain: str = ""


@dataclass()
class emailName:
    full: str = ""
    first: str = ""
    middle: str = ""
    last: str = ""


class keyType(Enum):
    OldTodo = 1
    OldStash = 2
    NewTodo = 3
    NewProcessed = 4


class eventType(Enum):
    SES = 1
    S3 = 2
    Lambda = 3
