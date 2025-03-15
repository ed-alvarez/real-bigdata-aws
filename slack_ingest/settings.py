"""Settings for the module"""
import logging
import os
from functools import cache  # use cache from 3.9 onwards

import boto3
import botocore
from boto3.session import Session
from dotenv import load_dotenv
from mypy_boto3_ssm import SSMClient

load_dotenv()
import helpers.file_io  # noqa: E402

aws_session = Session()
ssm_client: SSMClient = aws_session.client("ssm")
log = logging.getLogger(__name__)
# TODO DELETE:
#  RELEASE_STATUS = 'dev'
#  OUTDIR = './archive'


TEMPDIR = "/tmp/slack/"
helpers.file_io.ensure_dir(TEMPDIR)  # doesn't seem to have any effect on lambda

SLACK_EXPORT_DOWNLOAD_PATH = "/tmp/slack/exports/"

LOG_LEVEL = os.environ.get("LOGGING_LEVEL", "INFO")
BOTO_LOG_LEVEL = os.environ.get("BOTO_LOGGING_LEVEL", "INFO")

ROLE_ARN = os.getenv("ROLE_ARN")

EXPORTDL_STEP_FN_ARN = os.getenv(
    "EXPORTDL_STEP_FN_ARN",
    "arn:aws:states:eu-west-1:955323147179:stateMachine:slackExportDlStateMachine-dev",
)


@cache  # Save on ssm access fees by memoizing
def get_client_parameter(client_name: str, parameter_name: str) -> str:
    result: str = ssm_client.get_parameter(Name=f"/slack/{client_name}/{parameter_name}", WithDecryption=True)["Parameter"]["Value"]
    log.debug(result)
    return result


def get_slack_api_token(client_name: str) -> str:
    result: str = get_client_parameter(client_name=client_name, parameter_name="SLACK_API_TOKEN")
    log.debug(result)
    return result


def try_get_slack_api_token(client_name: str) -> str:
    # Ok if no slack api token exists for client
    result: str = ""
    try:
        result = get_client_parameter(client_name=client_name, parameter_name="SLACK_API_TOKEN")
        log.debug(result)
    except botocore.exceptions.ClientError as ce:
        if "ParameterNotFound" in str(ce):
            log.warning(ce)
            pass
        else:
            log.exception(ce)
            raise (ce)
    return result


def get_slack_email_login(client_name: str) -> str:
    result: str = get_client_parameter(client_name=client_name, parameter_name="SLACK_EMAIL_LOGIN")
    log.debug(result)
    return result


def get_slack_password(client_name: str) -> str:
    result: str = get_client_parameter(client_name=client_name, parameter_name="SLACK_PASSWORD")
    log.debug(result)
    return result


def get_slack_team_name(client_name: str) -> str:
    return get_client_parameter(client_name=client_name, parameter_name="SLACK_TEAM_NAME")


def try_get_slack_otp_secret(client_name: str) -> str:
    # Ok if no slack otp secret exists for client
    result: str = ""
    try:
        result = get_client_parameter(client_name=client_name, parameter_name="SLACK_OTP_SECRET")
        log.debug(result)
    except botocore.exceptions.ClientError as ce:
        if "ParameterNotFound" in str(ce):
            log.warning(ce)
            pass
        else:
            log.exception(ce)
            raise (ce)
    return result


SLACK_API_LIMIT_SIZE = None  # API calls limit batch size. Used during testing to ensure pagination is working

# Get ES Credentials direct from AWS Parameter Store rather than env variables
stage = os.getenv("STAGE", "dev")
if stage is None:
    err_str: str = "Stage environment variable was not set!"
    log.exception(err_str)
    raise Exception(err_str)

ES_INPUT_INDEX = ssm_client.get_parameter(Name=f"/elastic_app/{stage}/slack/index")["Parameter"]["Value"]
ES_HOST = ssm_client.get_parameter(Name=f"/elastic_cluster/{stage}")["Parameter"]["Value"]
ES_USER = ssm_client.get_parameter(Name=f"/elastic_app/{stage}/slack/user")["Parameter"]["Value"]
ES_PASSWORD = ssm_client.get_parameter(Name=f"/elastic_app/{stage}/slack/password", WithDecryption=True)["Parameter"]["Value"]

ES_CONNECTION = {}
ES_CONNECTION["hosts"] = ES_HOST
ES_CONNECTION["http_auth"] = (ES_USER, ES_PASSWORD)
ES_CONNECTION["scheme"] = "https"
ES_CONNECTION["timeout"] = 60
ES_CONNECTION["port"] = 9243
ES_CONNECTION["verify_certs"] = True
log.debug(ES_CONNECTION)

ES_PIPELINE = "slack-parse"
ES_OP_TYPE = "create"  # Use index to update record if found

ES_UPLOAD_BATCH_SIZE = int(os.getenv("ES_UPLOAD_BATCH_SIZE", 500))
ES_UPLOAD_MAX_SIZE_MB = float(os.getenv("ES_UPLOAD_MAX_SIZE_MB", 5))
LAMBDA_MIN_TIME_REQUIRED_SECS = int(os.getenv("LAMBDA_MIN_TIME_REQUIRED_SECS", 90))

TIKA_SERVER_JAR = os.getenv("TIKA_SERVER_JAR")

FINGERPRINTDB_HOST = os.getenv("FINGERPRINTDB_HOST")
FINGERPRINTDB_PORT = int(os.getenv("FINGERPRINTDB_PORT", -1))
FINGERPRINTDB_USER = os.getenv("FINGERPRINTDB_USER")
FINGERPRINTDB_REGION = os.getenv("FINGERPRINTDB_REGION")
FINGERPRINTDB_DBNAME = os.getenv("FINGERPRINTDB_DBNAME")

""" TODO DELETE
CREATE_JSON_BACKUP = os.environ.get('CREATE_JSON_BACKUP', 0)

S3_BUCKET_TOD = '.'.join([RELEASE_STATUS, 'todo.slack'])
S3_BUCKET_PROCESSED = '.'.join([RELEASE_STATUS, 'processed.slack'])
S3_BUCKET_ARCHIVED = '.'.join([RELEASE_STATUS, 'archive.slack'])

MSG_TYPE = 'slack'
"""

IGNORE_FILE_EXTENSIONS = ["AdvertisingBranding"]
GRAPHICS_FILE_EXTENSIONS = ["gif", "png", "bmp", "jpg"]
AUDIO_FILE_EXTENSIONS = ["mp3", "mpeg", "wav", "aif"]
ENCRYPTED_FILE_EXTENSIONS = ["pgp"]
COMPRESSED_FILE_EXTENSIONS = ["zip", "tar", "7z", "bz2", "gz", "rar"]

ignore_list_members = []
ignore_list_members.append(IGNORE_FILE_EXTENSIONS)
ignore_list_members.append(GRAPHICS_FILE_EXTENSIONS)
ignore_list_members.append(AUDIO_FILE_EXTENSIONS)
ignore_list_members.append(COMPRESSED_FILE_EXTENSIONS)
ignore_list_members.append(ENCRYPTED_FILE_EXTENSIONS)
ATTACHMENTS_IGNORE_LIST = [item for sublist in ignore_list_members for item in sublist]

ARCHIVE_EXTENSION = "zip"  # "tgz"
