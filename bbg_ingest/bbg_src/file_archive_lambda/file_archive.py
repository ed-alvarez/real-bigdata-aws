"""
Archive All BBG files to the Archive Directory

  The input event message is

  {
  "bbg_client_id": "mc886353171",
  "client_name": "mirabella"
  "bbg_manifest" : <"DAILY" | 'ARCHIVE'>
  }
"""
import logging
import os
from typing import List

import aws_lambda_logging
from bbg_helpers.helper_dataclass import BbgFiles

from shared.shared_src.s3.s3_helper import S3Helper

log_level = os.environ.get("LOGGING_LEVEL", "INFO")
boto_log_level = os.environ.get("BOTO_LOGGING_LEVEL", "INFO")
log = logging.getLogger()


def lambda_handler(event, context):
    aws_lambda_logging.setup(level=log_level, boto_level=boto_log_level, aws_request_id=context.aws_request_id, module="%(module)s")
    log.info("Start File Archive")
    log.info(event)

    file_archive(event)

    log.info("End File Archive")


def generate_directory_prefix(file_name: str) -> str:
    directory_parts: List = file_name.split("/")
    directory_prefix: str = f"{directory_parts[0]}/{directory_parts[1]}/"
    return directory_prefix


def generate_example_file(bbg_params: BbgFiles) -> str:
    example_file: str = ""
    if bbg_params.IB_file_name:
        example_file = bbg_params.IB_file_name
    elif bbg_params.MSG_file_name:
        example_file = bbg_params.MSG_file_name
    elif bbg_params.MSG_ATT_file_name:
        example_file = bbg_params.MSG_ATT_file_name
    elif bbg_params.IB_ATT_file_name:
        example_file = bbg_params.IB_ATT_file_name
    return example_file


def file_archive(event):
    log.debug("file_archive {}".format(event))
    bbg_params: BbgFiles = BbgFiles(**event["bbg_files"])
    s3_client: S3Helper = S3Helper(client_name=event["client_name"], ingest_type="bbg")
    example_file: str = generate_example_file(bbg_params=bbg_params)
    # Generate List of Files to Copy
    directory_with_date: str = generate_directory_prefix(file_name=example_file)

    # Generate list of objects
    directory_keys = s3_client.list_files_with_prefix(prefix=directory_with_date)

    # Loop through list of objects and copy to destination
    delete_list = []
    for key in directory_keys:
        s3_client.copy_file_between_folders(src_key=key, dst_key=key.replace("todo.bbg", "processed.bbg"))
        s3_client.copy_file_between_folders(src_key=key, dst_key=key.replace("todo.bbg", "archive.bbg"))
        delete_list.append({"Key": key})

    # Add directory key back in to delete
    delete_list.append({"Key": directory_with_date})

    # Remove files from Origin
    s3_client.delete_list_of_objects(list_of_objects_to_delete=delete_list)
