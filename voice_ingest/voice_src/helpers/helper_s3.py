from logging import getLogger
from typing import Dict

from boto3 import client
from botocore.exceptions import ClientError, ParamValidationError
from voice_settings import processingStage

log = getLogger()


class s3Helper:
    def __init__(self, s3_client=None):
        self._s3_client: client = s3_client or client("s3")
        self._file_content: str = ""

    @property
    def fileContent(self) -> str:
        return self._file_content

    def get_file_body_from_s3(self, s3_details):
        try:
            file_contents: Dict = self._s3_client.get_object(**s3_details)
            self._file_content = file_contents["Body"].read().decode("utf-8")

        except ParamValidationError as ex:
            log.debug("FAIL get object %s", s3_details["Key"])
            log.exception(f'Param Validation Error retrieving {s3_details["Key"]}. Reason : {ex}')
            log.debug("Exit get_file with Error")
            raise ex

        except ClientError as ex:
            log.debug("FAIL get object %s", s3_details["Key"])
            log.exception(f'Client Error retrieving {s3_details["Key"]}. Reason : {ex}')
            log.debug("Exit get_file with Error")
            raise ex

        return self._file_content

    def copy_object(self, file_key: str, bucket: str, from_root: processingStage, to_root: processingStage):
        copy_source = {"Bucket": bucket, "Key": file_key}

        key_destination = file_key.replace(from_root.value, to_root.value)
        log.info(f"Copy {file_key} to {key_destination}")

        try:
            self._s3_client.copy(copy_source, Bucket=bucket, Key=key_destination)
            log.debug(f"Copied to {key_destination}")
        except Exception as e:
            log.error("Error = " + str(e))
            log.debug(f"Have not copied {file_key} to {key_destination}")
            raise e
        return self

    def move_object_between_roots(self, file_key: str, bucket: str, from_root: processingStage, to_root: processingStage):
        self.copy_object(file_key=file_key, bucket=bucket, from_root=processingStage.todo, to_root=processingStage.processed)
        try:
            self._s3_client.delete_object(Bucket=bucket, Key=file_key)
            log.debug(f"DELETED {file_key}")
        except Exception as e:
            log.error("Error = " + str(e))
            log.debug(f"Have not deleted {file_key}")
            raise e
        return self
