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
from shared.shared_src.helper_aws_parameters import AWS_Key_Parameters

CLIENT = "ips"
INGEST_SOURCE = "teams"
LOG_FORMAT = "%(asctime)s -%(levelname)s - %(module)s:%(funcName)s::ln.%(lineno)s:: >%(message)s<"
STAGE = os.environ.get("STAGE", "dev")
LAUNCH_LAMBDA_NAME = f"{STAGE}-MSTeams-step-fn-launch"
DYNAMO_DB_TABLE = os.environ.get("DYNAMO_DB_TABLE", f"{STAGE}-msTeamsIngest")
UPLOAD_TO_ES = bool(int(os.environ.get("PUSH_ES", 1)))
Write_User_Data_To_File = os.environ.get("SAVE_USER_CHAT", "yes")
ENV_TENANT = f"{STAGE}/{INGEST_SOURCE}"  # DEV/ZOOM | PROD/ZOOM

AWS_ACCOUNT = "955323147179" if "prod" in STAGE else "899631935537"

SF_ARN: str = f"arn:aws:states:eu-west-1:{AWS_ACCOUNT}:stateMachine:{STAGE}-ingest-teams-state-machine"


uPNList = [
    "james@ip-sentinel.com",
    "tom@ip-sentinel.com",
    "mike@ip-sentinel.com",
    "brielle@fingerprint-supervision.com",
    "sean@fingerprint-supervision.com",
    "rob@fingerprint-supervision.com",
    "anthony@fingerprint-supervision.com",
]

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
BOTO_LOG_LEVEL = os.environ.get("BOTO_LOG_LEVEL", "INFO")
FINGERPRINT_TYPE = "teams.personal"

MSG_TYPE = "email"

PROJ_PATH = Path(__file__).parent

IGNORE_FILE_EXTENSIONS = ["AdvertisingBranding"]
# GRAPHICS_FILE_EXTENSIONS = ['gif', 'png', 'bmp', 'jpg']
GRAPHICS_FILE_EXTENSIONS = ["gif", "bmp", "jpg"]
AUDIO_FILE_EXTENSIONS = ["mp3", "mpeg", "wav", "aif"]
ENCRYPTED_FILE_EXTENSIONS = ["pgp"]
COMPRESSED_FILE_EXTENSIONS = ["zip", "tar", "7z", "bz2", "gz" "rar"]


class eventSource(Enum):
    S3 = "s3"
    TEAMS = "teams"


class eventPeriod(Enum):
    daily = "daily"
    HISTORY = "history"


class fileStore(Enum):
    S3 = "s3"
    Local = "local"


class processingStage(Enum):
    todo = "todo"
    processed = "processed"
    archived = "archived"


FILE_STORE = fileStore.S3.value

AWS_TIMEOUT_MILLISECONDS = int(os.environ.get("AWS_TIMEOUT_MILLISECONDS", 60000))
MESSAGE_BATCH_SIZE = int(os.environ.get("MESSAGE_BATCH_SIZE", 10000))
MESSAGE_LIST_SIZE = int(os.environ.get("MESSAGE_LIST_SIZE", 5000000))
UPLOAD_TO_ES = os.environ.get("UPLOAD_TO_ES", True)  # True

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

ES_INDEX = os.environ.get("ES_INDEX", "ips_data_input_teams")
ES_OP_TYPE = os.environ.get("ES_OP_TYPE", "index")

STEP_FN_ARN = os.environ.get("STEP_FN_ARN", "")
