import os
from dataclasses import dataclass
from typing import Dict

import boto3
from dotenv import load_dotenv

load_dotenv()
from enum import Enum

CLIENT = "ips"

LOG_LEVEL = os.environ.get("LOGGING_LEVEL", "INFO")
BOTO_LOG_LEVEL = os.environ.get("BOTO_LOGGING_LEVEL", "INFO")

STAGE = os.environ.get("STAGE", "dev")


class eventType(Enum):
    SES = "ses"
    S3 = "s3"
    Lambda = "lambda"
    manual = "manual"


class transcribeType(Enum):
    channel = "channel"
    speaker = "speaker"


class cdrType(Enum):
    redbox = "redbox"
    ringcentral = "ringcentral"
    freeswitch = "freeswitch"
    verba = "verba"


ES_CONNECTION = {}
ES_CONNECTION["hosts"] = os.getenv("ES_HOST")
ES_CONNECTION["http_auth"] = (os.getenv("ES_USER"), os.getenv("ES_PASSWORD"))
ES_CONNECTION["scheme"] = "https"
ES_CONNECTION["timeout"] = 60
ES_CONNECTION["port"] = 9243
ES_CONNECTION["verify_certs"] = True

ES_OP_TYPE = "create"  # Use index to update record if found
INPUT_INDEX = "ips_data_input_voice"

DYNAMO_DB_TABLE = os.environ.get("DYNAMO_DB_TABLE", "dev_voiceIngest")
AWS_TRANSCRIBE_PROFILE = "ProcessTranscriptRole"

if STAGE == "dev":
    ENRICH_PHRASES = False
else:
    ENRICH_PHRASES = True

transcribe_boto = {
    transcribeType.channel.value: {"ChannelIdentification": True},
    transcribeType.speaker.value: {
        "MaxSpeakerLabels": 10,
        "ShowSpeakerLabels": True,
    },
}

MSG_TYPE = "voice"


class processingStage(Enum):
    todo = "todo"
    processed = "processed"
    archived = "archived"
