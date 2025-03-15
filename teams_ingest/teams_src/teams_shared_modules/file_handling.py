from __future__ import annotations

import json
import logging
from pathlib import PosixPath
from typing import ClassVar, Dict, List, Type

import boto3
from botocore.exceptions import ClientError
from teams_settings import processingStage
from teams_src.teams_shared_modules.paths_helper_functions import _generate_teams_stage

log = logging.getLogger()


class FileHandling:
    _registry: ClassVar[Dict[str, Type[FileHandling]]] = {}

    def __init_subclass__(cls, name: str, **kwargs) -> None:
        cls.name: str = name  # type: ignore
        FileHandling._registry[name] = cls
        super().__init_subclass__(**kwargs)  # type: ignore

    def __init__(self, file_name: str = "", client: str = "") -> None:
        super().__init__()
        self.client: str = client
        self.file_name: str = file_name

    @classmethod
    def get(cls, name: str):
        return FileHandling._registry[name]

    def save_json(self, data: List[Dict]) -> FileHandling:
        raise NotImplementedError()

    def load_json(self) -> List[Dict]:
        raise NotImplementedError()

    def save_item_to_store(self, data: bytes) -> FileHandling:
        raise NotImplementedError()

    def _save_file(self, data: List[Dict]) -> FileHandling:
        raise NotImplementedError()

    def move_message_to_processed_bucket(self, file_key: str) -> FileHandling:
        raise NotImplementedError()

    def copy_to_archive(self) -> FileHandling:
        raise NotImplementedError()


class LocalFileHandling(FileHandling, name="local"):
    def __init__(self, file_name: str = "", client: str = ""):
        super().__init__(file_name, client)

    def _make_directory_for_file(self, file_name: str) -> None:
        posix_parent: PosixPath = PosixPath(file_name).parent
        posix_parent.mkdir(parents=True, exist_ok=True)
        return

    def _save_file(self, data: List[Dict]) -> LocalFileHandling:
        self._make_directory_for_file(file_name=self.file_name)
        with open(self.file_name, "w") as jsonfile:
            json.dump(data, jsonfile, indent=4)
        return self

    def save_json(self, data: List[Dict]) -> LocalFileHandling:
        self._save_file(data=data)
        return self


class S3FileHandling(FileHandling, name="s3"):
    def __init__(self, file_name: str = "", client: str = ""):
        super().__init__(file_name, client)
        try:
            log.debug("Initialising S3FileHandling Instance...")
            self._s3_client = boto3.client("s3")

        except ClientError as ex:
            log.exception("S3FileHandling class initialisation failed!")
            raise ex

    def _generate_bucket_name(self) -> str:
        return f"{self.client}.ips"

    def save_item_to_store(self, data: bytes) -> S3FileHandling:
        try:
            result = self._s3_client.put_object(
                Bucket=self._generate_bucket_name(), Key=self.file_name, Body=data  # Note: NO .gz extension!
            )
        except Exception as e:
            log.error("Error = " + str(e))
            log.debug(f"Have not saved {self.file_name} to S3")
        return self

    def _get_date_from_filename(self, file_name: str) -> str:
        file_parts: List = file_name.split("/")
        date_dir: str = file_parts[1]
        return date_dir

    def _generate_prefix(self, stage: processingStage, file_name: str):
        date_dir: str = self._get_date_from_filename(file_name=file_name)
        root: str = _generate_teams_stage(processing_stage=stage)
        s3_prefix: str = ("/").join([root, date_dir])
        return s3_prefix

    def copy_to_archive(self) -> S3FileHandling:

        s3_prefix: str = self._generate_prefix(stage=processingStage.processed, file_name=self.file_name)
        s3_bucket = self._generate_bucket_name()

        try:
            list_of_objects: list = self._s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)["Contents"]
        except Exception as ex:
            error_msg = f"No Contents Key for prefix {s3_prefix} in {s3_bucket}"
            log.exception(error_msg)
            raise ValueError(error_msg)

        # copy each file to archived directory
        for object in list_of_objects:
            self._copy_object(file_key=object["Key"], from_root=processingStage.processed, to_root=processingStage.archived)

        return self

    def move_message_to_processed_bucket(self, file_key: str) -> S3FileHandling:
        self._move_object_between_roots(file_key=file_key, from_root=processingStage.todo, to_root=processingStage.processed)
        return self

    def _copy_object(self, file_key: str, from_root: processingStage, to_root: processingStage) -> S3FileHandling:
        copy_source = {"Bucket": self._generate_bucket_name(), "Key": file_key}

        key_destination = file_key.replace(from_root.value, to_root.value)
        log.info(f"Copy {file_key} to {key_destination}")

        try:
            self._s3_client.copy(copy_source, Bucket=self._generate_bucket_name(), Key=key_destination)
            log.debug(f"Copied to {key_destination}")
        except Exception as e:
            log.error("Error = " + str(e))
            log.debug(f"Have not copied {file_key} to {key_destination}")
            raise e
        return self

    def _move_object_between_roots(self, file_key: str, from_root: processingStage, to_root: processingStage) -> S3FileHandling:
        self._copy_object(file_key=file_key, from_root=processingStage.todo, to_root=processingStage.processed)
        try:
            self._s3_client.delete_object(Bucket=self._generate_bucket_name(), Key=file_key)
            log.debug(f"DELETED {file_key}")
        except Exception as e:
            log.error("Error = " + str(e))
            log.debug(f"Have not deleted {file_key}")
            raise e
        return self

    def save_json(self, data: List[Dict]) -> S3FileHandling:
        try:
            result = self._s3_client.put_object(Body=str(json.dumps(data)), Bucket=self._generate_bucket_name(), Key=self.file_name)
        except Exception as e:
            log.error("Error = " + str(e))
            log.debug(f"Have not saved {self.file_name} to s3")
            raise e

        return self

    def load_json(self) -> List[Dict]:
        try:
            data = self._s3_client.get_object(Bucket=self._generate_bucket_name(), Key=self.file_name)
            json_data: str = data["Body"].read().decode("utf-8")
            dict_data = json.loads(json_data)

        except Exception as e:
            log.error("Error = " + str(e))
            log.debug(f"Have not saved {self.file_name} to s3")
            raise e

        return dict_data
