import os
import sys
from enum import Enum
from pathlib import Path

tenant_directory = Path(__file__).resolve().parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))

from dotenv import load_dotenv

load_dotenv()

# ES CONFIGs
from shared.shared_src.helper_aws_parameters import AWS_Key_Parameters

# LAMBDA CONFIGs
STAGE = os.environ.get("STAGE", "dev")
CLIENT = os.environ.get("CLIENT", "melqart")

AWS_ACCOUNT = "955323147179" if "prod" in STAGE else "899631935537"

SF_ARN: str = f"arn:aws:states:eu-west-1:{AWS_ACCOUNT}:stateMachine:{STAGE}-ingest-zoom-state-machine"


INGEST_SOURCE = os.environ.get("", "zoom")
PUSH_ES = bool(int(os.environ.get("PUSH_ES", 1)))

LOG_LEVEL = os.environ.get("LOGGING_LEVEL", "INFO")
BOTO_LOG_LEVEL = os.environ.get("BOTO_LOGGING_LEVEL", "INFO")

ENV_TENANT = f"{STAGE}/{INGEST_SOURCE}"  # DEV/ZOOM | PROD/ZOOM

# ZOOM ENDPOINTS
USER = "/users/{user_id}"
USERS = "/users"

# MEETINGS
MEETING_DETAIL = "/past_meetings/{meeting_id}"
MEETINGS_RECORDINGS = "/meetings/{meeting_id}/recordings"
MEETING_PARTICIPANTS = "/past_meetings/{meeting_id}/participants"

# CLOUD RECORDINGS
RECORDINGS = "/users/{user_id}/recordings"
DOWNLOAD = "{download_url}?access_token={JWT}"

# PHONE
PHONE_CALL_LOGS = "/phone/call_logs"
PHONE_CALL_LOG_DETAIL = "/phone/call_logs/{call_log_id}"
PHONE_RECORDINGS = "/phone/call_logs/{call_id}/recordings"
PHONE_TRANSCRIPT_DOWNLOAD = "/phone/recording_transcript/download/{recording_id}"

ES_USER = os.getenv(
    "ES_USER",
    AWS_Key_Parameters(client_name="elastic_app").get_parameter_value(item_key=f"{ENV_TENANT}/user"),
)
ES_PASSWORD = os.getenv(
    "ES_PASSWORD",
    AWS_Key_Parameters(client_name="elastic_app").get_parameter_value(item_key=f"{ENV_TENANT}/password"),
)
ES_CLOUD_ID = os.getenv(
    "ES_CLOUD_ID",
    AWS_Key_Parameters(client_name="elastic_app").get_parameter_value(item_key=f"{ENV_TENANT}/cloud_id"),
)
INPUT_INDEX = os.getenv(
    "ES_INDEX",
    AWS_Key_Parameters(client_name="elastic_app").get_parameter_value(item_key=f"{ENV_TENANT}/index"),
)
ES_OP_TYPE = "create"


class BucketStage(Enum):
    TODO = "todo"
    PROCESS = "processed"
    ARCHIVED = "archived"


class zoomType(Enum):
    call = "call"
    meet = "meet"


class FileExtension(Enum):
    MP3 = "mp3"
    VTT = "vtt"
    M4A = "m4a"
    JSON = "json"
