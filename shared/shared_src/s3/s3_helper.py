"""
Helper file for s3 Functions
"""
import datetime
import functools
import json
import logging
import os
import time
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.exceptions import BotoCoreError, ClientError, ParamValidationError

from shared.shared_src.utils import timing

log = logging.getLogger()


def catch_boto_errors(func):
    @functools.wraps(func)
    def _wrapper_decorator(*args, **kwargs):
        value = None
        try:
            value = func(*args, **kwargs)
        except ParamValidationError as ex:
            log.exception("Boto ParamValidationError error: %s" % ex)
            raise
        except ClientError as ex:
            log.exception("Boto ClientError error: %s" % ex)
            raise
        except BotoCoreError as ex:
            log.exception("Boto BotoCoreError error: %s" % ex)
            raise
        return value

    return _wrapper_decorator


class S3Helper:
    def __init__(self, client_name: str, ingest_type: str, s3_client=None):
        self.s3_client = s3_client or boto3.client("s3")
        self._client_name: str = client_name
        self._ingest_type: str = ingest_type
        self._bucket_name: str = f"{self._client_name}.ips"
        self._bucket_type: str = "todo"  # Acting as the default bucket type

    @property
    def clientName(self):
        return self._client_name

    @property
    def bucketName(self):
        return self._bucket_name

    @staticmethod
    def _is_dev() -> bool:
        if os.environ.get("STAGE") == "dev":
            return True

    @staticmethod
    def _str_list_to_binary_file(str_list: List) -> str:
        binary_file: str = ""
        for item in str_list:
            binary_file = binary_file + ("%s\n" % item)
        return binary_file

    def datetime_to_directory_format(self, date_dt: datetime) -> str:
        return datetime.datetime.strftime(date_dt, "%Y-%m-%d")

    @catch_boto_errors
    def _s3_list_objects(self, bucket: str, prefix: str) -> Dict:
        response: Dict = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return response

    @timing
    def list_files_with_prefix(self, prefix):
        log.debug(f"list_files_with_prefix, prefix, {prefix}")
        """List files in specific S3 URL"""
        response = self._s3_list_objects(bucket=self._bucket_name, prefix=prefix)
        return [content.get("Key") for content in response.get("Contents", []) if content["Size"] > 0]

    @catch_boto_errors
    def _s3_put_object(self, body, bucket: str, key: str) -> Dict:
        result: dict = self.s3_client.put_object(Body=body, Bucket=bucket, Key=key)
        return result

    @timing
    def write_file_to_s3(self, file_key: str, file_content: bytes) -> Dict:
        log.debug(f"write_file_to_s3, file_key, {file_key}")
        result: Dict = self._s3_put_object(body=file_content, bucket=self._bucket_name, key=file_key)
        return result

    @timing
    def write_files_to_retrieve_to_s3(self, file_list: List, file_name: str) -> Dict:
        log.debug(f"write_files_to_retrieve_to_s3, {file_list}, file_name, {file_name}")
        s3_file_name: str = self._generate_file_key(file_name)
        log.debug("write_files_to_retrieve_to_s3, -> {s3_file_name}")
        file_body = self._str_list_to_binary_file(file_list)
        result: Dict = self._s3_put_object(body=file_body, bucket=self._bucket_name, key=s3_file_name)
        log.debug("Put Binary File")
        return result

    @catch_boto_errors
    def _s3_get_object(self, bucket: str, key: str) -> Dict:
        result: Dict = self.s3_client.get_object(Bucket=bucket, Key=key)
        return result

    @timing
    def get_file_content(self, file_key: str, as_dict: bool = False) -> Union[bytes, Dict]:
        log.info(f"Downloading file {file_key} from bucket {self._bucket_name}")
        file_contents = self._s3_get_object(bucket=self._bucket_name, key=file_key)

        if as_dict:
            return json.loads(file_contents["Body"].read().decode())
        else:
            return file_contents["Body"].read()

    @timing
    def get_file_body_with_utf_correction(self, file_key) -> bytes:
        file_content = None
        body = None
        file_content = self.get_file_content(file_key=file_key)
        try:
            body = file_content.decode("utf-8")
        except Exception as ex:
            log.warning(f"issue with UTF8 encoding of email so trying char by char: {ex}")
            body = "".join(chr(x) for x in file_content)
        log.debug("Email body read")
        return body

    @catch_boto_errors
    def _s3_copy(self, copysource: Dict, bucket: str, key: str) -> Dict:
        response: Dict = self.s3_client.copy(CopySource=copysource, Bucket=bucket, Key=key)
        return response

    @timing
    def copy_file_between_folders(self, src_key, dst_key):
        success_copy = False
        log.debug(f"copy_file_between_folders, src_key, {src_key}, dst_key, {dst_key}")
        source_obj = {
            "Bucket": self._bucket_name,
            "Key": src_key,
        }
        try:
            self._s3_copy(copysource=source_obj, bucket=self._bucket_name, key=dst_key)
            success_copy = True
        except Exception as error:
            log.error(f"Error copying files {error}")
        return success_copy

    @timing
    @catch_boto_errors
    def delete_file(self, file_key):
        log.debug(f"Deleting from {self._bucket_name} file_key {file_key} at stage {self._bucket_type}")
        self.s3_client.delete_object(Bucket=self._bucket_name, Key=file_key)
        log.info(f"Succes deleting {self._bucket_name} file_key {file_key} at stage {self._bucket_type}")

    @timing
    def copy_file_between_buckets(self, source_bucket, destination_bucket, file_key):
        log.debug(
            "copy_file_between_buckets, source_bucket, {}, destination_bucket, {}, file_key, {}".format(
                source_bucket,
                destination_bucket,
                file_key,
            ),
        )
        source_obj = {
            "Bucket": source_bucket,
            "Key": file_key,
        }
        return self._s3_copy(copysource=source_obj, bucket=destination_bucket, key=file_key)

    @catch_boto_errors
    def _s3_delete_objects(self, bucket: str, delete: Dict) -> Dict:
        response: Dict = self.s3_client.delete_objects(Bucket=bucket, Delete=delete)
        return response

    @timing
    def delete_list_of_objects(self, list_of_objects_to_delete: List, bucket: str = "") -> Dict:
        log.debug(
            "delete_list_of_objects, list_of_objects_to_delete, {}, bucket, {}".format(
                list_of_objects_to_delete,
                bucket,
            ),
        )
        bucket_name: str = ""
        bucket_name = bucket or self._bucket_name
        delete_obj: Dict = {
            "Objects": list_of_objects_to_delete,
        }
        response: Dict = self._s3_delete_objects(bucket=bucket_name, delete=delete_obj)
        return response

    def _obj_to_bytes(self, obj: Any) -> Any:
        if isinstance(obj, bytes):
            return obj
        elif isinstance(obj, (dict, list)):
            return json.dumps(obj).encode("UTF-8")
        else:
            return json.dumps(asdict(obj)).encode("UTF-8")

    def to_json(self, file: bytes):
        file: str = file.decode("utf-8")
        file: str = json.loads(file)
        return file

    def _create_full_file_key(self, bucket_stage, ingest_source, file_name, extension):
        self._bucket_type = bucket_stage or self._bucket_type
        self._ingest_type = ingest_source or self._ingest_type
        if self._is_dev():
            return f"dev-{self._bucket_type}.{self._ingest_type}/{file_name}.{extension}"
        else:
            return f"{self._bucket_type}.{self._ingest_type}/{file_name}.{extension}"

    def _create_file_name(self, file_name: str, date_from_event: str) -> str:
        ts_ms: time = int(time.time() * 1000)
        if type(date_from_event) is not str:
            formatted_date: datetime = date_from_event.strftime("%Y-%m-%d")
        elif type(date_from_event) is str:
            date = datetime.strptime(date_from_event, '%Y-%m-%d')
            formatted_date: datetime = date.strftime("%Y-%m-%d")
        else:
            formatted_date: datetime = datetime.date.today().strftime("%Y-%m-%d")
        return f"{formatted_date}/{file_name}_{ts_ms}"

    @catch_boto_errors
    def lamda_write_to_s3(
        self,
        obj: Any,
        ingest_source: str = "",
        extension: str = "json",
        bucket_stage: str = "",
        file_name: str = "",
        date_from_event: Optional[str] = None,
    ) -> str:

        file_name: str = self._create_file_name(file_name=file_name, date_from_event=date_from_event)
        full_file_key: str = self._create_full_file_key(bucket_stage, ingest_source, file_name, extension)
        obj_to_bytes: Any = self._obj_to_bytes(obj)
        log.info(f"S3 Bucket {self._bucket_name} WRITING {full_file_key} | For Obj {type(obj)}")
        self.write_file_to_s3(file_key=full_file_key, file_content=bytes(obj_to_bytes))
        return full_file_key
