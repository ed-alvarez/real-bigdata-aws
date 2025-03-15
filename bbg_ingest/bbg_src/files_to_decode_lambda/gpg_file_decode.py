import logging
import os
from typing import BinaryIO

import bbg_settings
import boto3

from shared.shared_src.gpg.gpg_decode import GPGHelper
from shared.shared_src.helper_aws_parameters import AWS_Key_Parameters
from shared.shared_src.s3.s3_helper import S3Helper

log_level = bbg_settings.LOG_LEVEL
boto_log_level = bbg_settings.BOTO_LOG_LEVEL
log = logging.getLogger()
if os.environ.get("AWS_EXECUTION_ENV") is None:
    ch = logging.StreamHandler()
    log.addHandler(ch)


class BBGGPGHelper:
    def __init__(self, client_name: str, s3_helper=None, ssm_helper=None):
        self._client_name: str = client_name
        self._s3_helper: S3Helper = s3_helper or S3Helper(client_name=self._client_name, ingest_type="bbg")
        self._aws_parameters: AWS_Key_Parameters = AWS_Key_Parameters(client_name=self._client_name)
        self._gpg_helper: GPGHelper = GPGHelper(
            client_name=self._client_name,
            passphrase_key=bbg_settings.PGP_PASSPHRASE_KEY,
            pem_file_key=bbg_settings.PGP_PEMFILE_KEY,
        )
        self._ssm_helper: ssm_helper = ssm_helper or boto3.client("ssm")
        self._decoded_file_name: str = ""

    @property
    def decodedFileName(self):
        return self._decoded_file_name

    def decode_file(self, decode_file_name, decoded_file_name):
        self._decoded_file_name = decoded_file_name
        file_encrypted_content: BinaryIO = self._s3_helper.get_file_content(file_key=decode_file_name)
        try:
            binary_file_contents: bytes = self._gpg_helper.decode_file(file_blob=file_encrypted_content)
        except KeyError as ex:
            log.exception(ex)
            raise ex
        self._s3_helper.write_file_to_s3(file_content=binary_file_contents, file_key=self._decoded_file_name)
