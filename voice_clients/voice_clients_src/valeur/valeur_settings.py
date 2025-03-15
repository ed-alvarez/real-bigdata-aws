import os
from logging import DEBUG

LOG_LEVEL = os.environ.get("LOGGING_LEVEL", DEBUG)
BOTO_LOG_LEVEL = os.environ.get("BOTO_LOGGING_LEVEL", DEBUG)
STAGE = os.environ.get("STAGE", "dev")
SSM_SFTP_HOST_KEY = os.environ.get("SSM_SFTP_HOST_KEY", "sftp-host")
SSM_SFTP_PORT_KEY = os.environ.get("SSM_SFTP_PORT_KEY", "sftp-port")
SSM_SFTP_ACCOUNT_ID_KEY = os.environ.get("SSM_SFTP_ACCOUNT_ID_KEY", "sftp-account")
SSM_SFTP_ACCOUNT_PASSWORD_KEY = os.environ.get("SSM_SFTP_ACCOUNT_PASSWORD_KEY", "sftp-password")
SSM_SFTP_KEY_KEY = os.environ.get("SSM_SFTP_KEY_KEY", "sftp-public-key")
SSM_SFTP_KEY_PASSCODE_KEY = os.environ.get("SSM_SFTP_KEY_PASSCODE_KEY", "sftp-public-key-passcode")
PGP_PEMFILE_KEY = os.environ.get("PGP_PEMFILE_KEY", "voice/gpgprivkey.pem")
PGP_PASSPHRASE_KEY = os.environ.get("PGP_PASSPHRASE_KEY", "voice/gpgprivkeypass")
INGEST_TYPE = "voice"
