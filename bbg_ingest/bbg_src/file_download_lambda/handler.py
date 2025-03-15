"""
Download BBG Files using SFTP to the todo S3 bucket
This module downloads the days Bloomberg files specified in the daily_manifest_current.txt
The files are downloaded to todo.[client].ips/bbg

  The input event message is

  {
  "bbg_client_id": "mc886353171",
  "client_name": "mirabella"
  "bbg_manifest" : <"DAILY" | 'ARCHIVE'>
  }

  The output event message is
  {
  "client_name": "mirabella",
  "files_downloaded" = ["bbg/<date>/<type>/<file_1>", .., "bbg/<date>/<type>/<file_n>"],
  "files_decoded" = "",
  "bucket_name" = "todo.<client>.ips",
  "has_files" : True
  }

"""

import logging

import aws_lambda_logging
import bbg_settings
from bbg_src.file_download_lambda.file_download import (
    BBGFileDownload,
    FileDownloadException,
)

log_level = bbg_settings.LOG_LEVEL
boto_log_level = bbg_settings.BOTO_LOG_LEVEL
log = logging.getLogger()


def lambda_handler(event, context):
    aws_lambda_logging.setup(level=log_level, boto_level=boto_log_level, aws_request_id=context.aws_request_id, module="%(module)s")
    log.info("Start File Download")
    log.debug('{"log_group_name" : "%s"}', context.log_group_name)
    log.debug('{"log_stream_name" : "%s"}', context.log_stream_name)
    log.info(event)

    result = ""
    file_download = BBGFileDownload(event=event)
    try:
        file_download.connect_classes()
    except FileDownloadException as ex:
        log.exception(ex)
        raise ex

    try:
        result = file_download.file_download()
    except Exception as ex:
        log.exception(ex)
        raise ex

    log.info(result)
    log.info("End File Download")
    return result
