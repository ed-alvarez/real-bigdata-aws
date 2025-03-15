"""
Helper file for s3 operations
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Tuple

import boto3
import botocore.exceptions
import helpers.file_io
import settings
from botocore.exceptions import ClientError, ParamValidationError

log = logging.getLogger()


def is_todo_path(path: str):
    # is_todo = 'todo.slack' in s3_path.split('/', 1)[0]
    return path.startswith("todo.slack") or path.startswith("dev.todo.slack")


def s3_file_exists(s3_client, bucket, key):
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            log.info(f"{key} doesnt exist")
            print(f"{key} doesn't exist")
            return False
        else:
            # Something else has gone wrong.
            raise
    else:
        # The object does exist.
        log.info(f"{key} already exists")
        print(f"{key} already exists")
        return True


class S3:
    def __init__(self, client_name, date_y_m_d, app_name="slack"):  # date = YYYY-MM-DD
        self.client_name = client_name
        self.bucket_name = f"{client_name}.ips"
        self.date_y_m_d = date_y_m_d

        self.archived_path = f"archived.{app_name}/{date_y_m_d}"
        self.processed_path = f"processed.{app_name}/{date_y_m_d}"
        self.todo_path = f"todo.{app_name}/{date_y_m_d}"

        if os.environ.get("STAGE") == "dev" or os.environ.get("AWS_EXECUTION_ENV") is None or os.environ.get("CIBUILD", None) == "1":
            self.todo_path = "dev." + self.todo_path
            self.processed_path = "dev." + self.processed_path
            self.archived_path = "dev." + self.archived_path

        # self._s3_todo_base_path = os.path.join(self.todo_path, self._s3_dir_date)

        try:
            log.debug("Initialising S3Object Instance...")
            self.s3_client = boto3.client("s3")

        except ClientError as ex:
            log.exception("S3Object class initialisation failed!")
            raise ex

    def delete_file(self, key):
        log.debug("delete_file, key, {}".format(key))

        try:
            response = self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
        except Exception as ex:
            raise ex
        return response

    def copy_file(self, source_key, dest_key):
        log.debug("copy_file_between_folders, src_key, {}, dst_key, {}".format(source_key, dest_key))
        source_obj = {
            "Bucket": self.bucket_name,
            "Key": source_key,
        }
        try:
            response = self.s3_client.copy_object(CopySource=source_obj, Bucket=self.bucket_name, Key=dest_key)
        except Exception as ex:
            raise ex
        return response

    def copy_file_from_todo_to_processed(self, todo_file_key):
        return self.copy_file_from_one_folder_to_another(todo_file_key, "todo", "processed")

    def copy_file_from_todo_to_unprocessed(self, todo_file_key):
        return self.copy_file_from_one_folder_to_another(todo_file_key, "todo", "unprocessed")

    def copy_file_from_processed_to_archived(self, processed_file_key):
        return self.copy_file_from_one_folder_to_another(processed_file_key, "processed", "archived")

    def copy_file_from_archived_to_processed(self, archived_file_key):
        return self.copy_file_from_one_folder_to_another(archived_file_key, "archived", "processed")

    def copy_file_from_todo_to_archived(self, todo_file_key):
        return self.copy_file_from_one_folder_to_another(todo_file_key, "todo", "archived")

    def copy_file_from_one_folder_to_another(self, file_key, _from, to):
        first, subfolder = file_key.split("/", 1)
        new_key = None
        if first == f"dev.{_from}.slack":
            new_key = os.path.join(f"dev.{to}.slack", subfolder)
        elif first == f"{_from}.slack":
            new_key = os.path.join(f"{to}.slack", subfolder)

        if new_key:
            return self.copy_file(file_key, new_key)

    def move_file_from_todo_to_processed(self, todo_file_key):
        res = self.copy_file_from_todo_to_processed(todo_file_key)

        # Clean up _todo files, leave if files from archived folder
        if todo_file_key.startswith("dev.todo.slack") or todo_file_key.startswith("todo.slack"):
            self.delete_file(todo_file_key)
        return res

    def move_file_from_todo_to_unprocessed(self, todo_file_key):
        res = self.copy_file_from_todo_to_unprocessed(todo_file_key)

        # Clean up _todo files, leave if files from archived folder
        if todo_file_key.startswith("dev.todo.slack") or todo_file_key.startswith("todo.slack"):
            self.delete_file(todo_file_key)
        return res

    def upload_msg_json_to_s3_processed_subfolder(self, channel_label, processed_local_path):
        s3_processed_subfolder = os.path.join("json-processed", "messages", channel_label)
        s3_processed_path = self.upload_files_to_s3_processed_subfolder([processed_local_path], s3_processed_subfolder)[0]
        return s3_processed_path

    def upload_files_to_s3_todo_subfolder(self, file_paths, sub_folder=None):
        path = os.path.join(self.todo_path, sub_folder) if sub_folder else self.todo_path
        return self.upload_files_to_s3(file_paths, path)

    # def upload_files_to_s3_todo_attachments(self, file_paths):
    #    return self.upload_files_to_s3_todo(file_paths, 'attachments')
    def upload_files_to_s3_archived_subfolder(self, file_paths, sub_folder=None):
        path = os.path.join(self.archived_path, sub_folder) if sub_folder else self.archived_path
        return self.upload_files_to_s3(file_paths, path)

    def upload_files_to_s3_processed_subfolder(self, file_paths, sub_folder=None):
        path = os.path.join(self.processed_path, sub_folder) if sub_folder else self.processed_path
        return self.upload_files_to_s3(file_paths, path)

    def upload_files_to_s3_todo_and_archived_subfolder(self, file_paths, sub_folder=None):
        """Upload file to s3 to-do section then copy to archived section"""
        todo_path = os.path.join(self.todo_path, sub_folder) if sub_folder else self.todo_path
        archived_path = os.path.join(self.archived_path, sub_folder) if sub_folder else self.archived_path
        todo_s3_files = self.upload_files_to_s3(file_paths, todo_path)
        for todo_key in todo_s3_files:
            archived_key = os.path.join(archived_path, os.path.basename(todo_key))
            self.copy_file(todo_key, archived_key)
        return todo_s3_files

    def upload_files_to_s3(self, file_paths, s3_folder):
        """location - to do,archived,processed"""
        log.debug("copy_files_from_tmp_to_s3, file_list, {}, s3_folder, {}".format(file_paths, s3_folder))
        s3_files = []
        for file in file_paths:
            key = os.path.join(s3_folder, os.path.basename(file))
            log.debug("copy_files_from_tmp_to_s3, file_name, {}, -> self.file_key, {}".format(file, key))
            s3_files.append(key)
            print(f"uploading to s3 {key}")
            try:
                self.s3_client.upload_file(Filename=file, Bucket=self.bucket_name, Key=key)
                log.debug("Put local file")
            except Exception as e:
                log.error(f"could not put file : {key} to bucket {self.bucket_name} Error = " + str(e))
                log.debug("Exit with Error Write to S3")
            print(f"deleting from local after s3 upload {file}")
            try:
                os.remove(file)
                log.debug(f"Removed {file} from tmp")
            except OSError as e:
                log.error("Error: %s - %s." % (e.filename, e.strerror))

        return s3_files

    def put_file_object_to_key(self, file_obj: bytes, key: str):
        return self.s3_client.put_object(
            Body=file_obj,
            Bucket=self.bucket_name,
            Key=key,
        )

    def check_metadata_file_exists(self, filename):
        # This method checks to see if a snapshot already exists for e.g. channels.json or
        # users.json, we only want to keep the earliest snapshot for each day
        archived_key = os.path.join(self.archived_path, filename)
        return s3_file_exists(self.s3_client, self.bucket_name, archived_key)

    def get_metadata(self):
        """Check to see if channels.json and users.json exists for this date"""
        archived_channels_key = os.path.join(self.archived_path, "json-slack", "channels.json")
        archived_users_key = os.path.join(self.archived_path, "json-slack", "users.json")

        try:
            channels = json.loads(self.get(archived_channels_key))
            users = json.loads(self.get(archived_users_key))
        except ClientError as ce:
            if ce.response["Error"]["Code"] == "NoSuchKey":
                channels_out, users_out = None, None
            else:
                raise Exception(f"Error while getting keys {archived_channels_key} and {archived_users_key}")
        else:
            # Transform array channels, users to be a dictionary with key id
            channels_out = {channel["id"]: channel for channel in channels}
            users_out = {user["id"]: user for user in users}

        return channels_out, users_out

    def get_messages_paths_from_folder(self, base_folder) -> list:
        """Returns a list of message_paths given base folder (e.g. todo_/archived folder)"""
        archived_messages_prefix = os.path.join(base_folder, "json-slack", "messages")
        paginator = self.s3_client.get_paginator("list_objects")
        operation_parameters = {
            "Bucket": self.bucket_name,
            "Prefix": archived_messages_prefix,
        }
        page_iterator = paginator.paginate(**operation_parameters)
        paths = []
        for page in page_iterator:
            if "Contents" in page:
                for item in page["Contents"]:
                    paths.append(item["Key"])

        return paths

    def get_messages_paths_from_archive(self):
        """Retrieve messages for specific date from archived folder, rather than looking in to-do
        for day-to-day jobs. For historical jobs."""
        return self.get_messages_paths_from_folder(self.archived_path)

    def get_messages_paths_from_todo(self) -> list:
        return self.get_messages_paths_from_folder(self.todo_path)

    def get(self, s3_key: str):
        """Gets content of file at s3_path"""
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
        return response["Body"].read()

    def download_attachment_to_tmp(self, attachment_id, is_todo=False):
        if is_todo:
            stage = "todo"
            s3_base_path = self.todo_path
        else:
            stage = "archived"
            s3_base_path = self.archived_path

        # os.path.join(s3_base_path, 'attachments', f'{attachment_id}.tgz')
        key = _get_attachment_s3_key(s3_base_path, attachment_id)
        local_path = os.path.join(
            settings.TEMPDIR,
            f"{stage}",
            "attachments",
            f"{attachment_id}.{settings.ARCHIVE_EXTENSION}",
        )
        helpers.file_io.ensure_dir(local_path)
        s3_client = boto3.client("s3")
        s3_client.download_file(self.bucket_name, key, local_path)
        return local_path

    def get_processed_s3_key_for_attachment(self, attachment_id):
        s3_base_path = self.processed_path
        return _get_attachment_s3_key(s3_base_path, attachment_id)

    def get_todo_s3_key_for_attachment(self, attachment_id):
        s3_base_path = self.todo_path
        return _get_attachment_s3_key(s3_base_path, attachment_id)

    def get_archived_s3_key_for_attachment(self, attachment_id):
        s3_base_path = self.archived_path
        return _get_attachment_s3_key(s3_base_path, attachment_id)

    def get_processed_s3_key_for_slack_messages_by_channel_label(self, channel_label):
        return f"{self.processed_path}/json-slack/messages/{channel_label}/{self.date_y_m_d}.json"

    def move_attachment_from_todo_to_processed(self, attachment_id: str):
        todo_key = os.path.join(self.todo_path, "attachments", f"{attachment_id}.tgz")
        return self.move_file_from_todo_to_processed(todo_key)


def _get_attachment_s3_key(s3_base_path, attachment_id):
    arc_ext = settings.ARCHIVE_EXTENSION  # tgz or zip
    return os.path.join(s3_base_path, "attachments", f"{attachment_id}.{arc_ext}")


def _get_metadata_for_date(client_name, base_date_y_m_d: str, day_offset=0):
    """Auxiliary function to return channels and users metadata for date and date offset to allow
    for easy searching"""
    date = datetime.strptime(base_date_y_m_d, "%Y-%m-%d")
    date_to_get = date + timedelta(days=day_offset)
    date_to_get_y_m_d = date_to_get.strftime("%Y-%m-%d")
    s3 = S3(client_name, date_to_get_y_m_d)
    return s3.get_metadata()


def get_closest_metadata(client_name: str, date_y_m_d: str) -> Tuple[dict, dict, bool]:
    """Search for and return closest date bucket containing users.json and channels.json in S3"""
    i = 0
    is_future = True
    # Get next day's, which will include channels created on current day. Otherwise will get errors for newly created channels
    # Get 2nd days, as we now have a 2 day gap between ingest day and day of export
    # As users can see conversation history of channels they're in, is also most accurate.
    channels, users = _get_metadata_for_date(client_name, date_y_m_d, 2)
    if channels is None or users is None:
        channels, users = _get_metadata_for_date(client_name, date_y_m_d, 1)

    while channels is None or users is None:
        # Search forward in time
        channels, users = _get_metadata_for_date(client_name, date_y_m_d, i)
        if i > 0:
            is_future = True
        if (channels is None or users is None) and i != 0:
            # Search backward in time
            channels, users = _get_metadata_for_date(client_name, date_y_m_d, -i)
            is_future = False
        i += 1
        if i > 59:
            raise Exception(f"Could not find metadata within 2 month range for {client_name}")

    return channels, users, is_future


def get_messages_for_date_from_archive(client_name: str, date_y_m_d: str):  # TODO move to s3.py
    """Retrieve messages for specific date from archived folder, rather than looking in to-do
    for day-to-day jobs. For historical jobs."""
    s3 = S3(client_name, date_y_m_d)
    return s3.get_messages_paths_from_archive()
