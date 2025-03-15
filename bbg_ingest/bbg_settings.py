"""Settings for the module"""
import os

from dotenv import load_dotenv

load_dotenv()
STAGE = os.environ.get("STAGE", "dev")
STEP_FN_ARN = os.environ.get("STEP_FN_ARN", "arn:aws:states:eu-west-1:955323147179:stateMachine:dev-parseBBGFiles")

LOG_LEVEL = os.environ.get("LOGGING_LEVEL", "INFO")
BOTO_LOG_LEVEL = os.environ.get("BOTO_LOGGING_LEVEL", "INFO")

DOWNLOAD_S3_CHUNK_SIZE = 6291456

ES_CONNECTION = {}
ES_CONNECTION["hosts"] = os.getenv("ES_HOST")
ES_CONNECTION["http_auth"] = (
    os.getenv("ES_USER"),
    os.getenv("ES_PASSWORD"),
)
ES_CONNECTION["scheme"] = "https"
ES_CONNECTION["timeout"] = 60
ES_CONNECTION["port"] = 9243
ES_CONNECTION["verify_certs"] = True

ES_OP_TYPE = "create"  # Use index to update record if found

# For File_Download
BBG_DAILY_MANIFEST = os.environ.get("BBG_DAILY_MANIFEST", "daily_manifest_current.txt")
BBG_ARCHIVE_MANIFEST = os.environ.get("BBG_ARCHIVE_MANIFEST", "Archive/daily_manifest_{yymmdd}.txt.gz")

S3_FOLDER_DOWNLOAD = "downloaded"

STORE_TYPE = os.environ.get("STORE_TYPE", "ssm")
SSH_HOST = os.environ.get("SSH_HOST", "ftpcom.bloomberg.com")
SSH_PORT = int(os.environ.get("SSH_PORT", 30206))
SSH_FILE_KEY = os.environ.get("SSH_FILE_KEY", "bbgsshkey.pem")
SSH_PASSPHRASE_KEY = os.environ.get("SSH_PASSPHRASE_KEY", "bbgsshkeypass")
SSH_PASSWORD_KEY = os.environ.get("SSH_PASSWORD_KEY", "bbgsshpass")

# For File_Decode
# use STORE_TYPE above
PGP_BINARY = os.environ.get("PGP_BINARY", "gpg")
PGP_PEMFILE_KEY = os.environ.get("PGP_PEMFILE_KEY", "bbgprivkey.pem")
PGP_PASSPHRASE_KEY = os.environ.get("PGP_PASSPHRASE_KEY", "bbgprivkeypass")

UPLOAD_TO_ES = os.environ.get("UPLOAD_TO_ES", True)  # True
BATCH_UPLOAD = os.environ.get("BATCH_UPLOAD", True)  # True


# http://tika.ip-sentinel.com:9998
LOCAL_TIKA = os.environ.get("LOCAL_TIKA", True)
TIKA_SERVER_ENDPOINT = os.environ.get("TIKA_SERVER_ENDPOINT", "http://localhost:9998")
TIKA_SERVER_JAR = "file:////tika_jar////tika-server-1.23.jar"

S3_BUCKET_TODO = "todo.email"
S3_BUCKET_PROCESSED = "processed.email"
S3_BUCKET_ARCHIVED = "archive.email"
