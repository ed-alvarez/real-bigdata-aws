"""
File to decode any Downloaded bloomberg files

This is part of a step function so keeps the state loop.

Input
{
  "client_name": "mirabella",
  "files_downloaded" = ["bbg/<date>/<type>/<file_1>", .., "bbg/<date>/<type>/<file_n>"],
  "files_decoded" = ["bbg/<date>/<type>/<file_1>", .., "bbg/<date>/<type>/<file_n>"],
  "bucket_name" = "todo.<client>.ips",
  }

Output
{
  "client_name": "mirabella",
  "files_downloaded" = ["bbg/<date>/<type>/<file_1>", .., "bbg/<date>/<type>/<file_n>"],
  "files_decoded" = ["bbg/<date>/<type>/<file_1>", .., "bbg/<date>/<type>/<file_n>"],
  "bucket_name" = "todo.<client>.ips",
  "more_to_process" : True | False
  }

"""
import logging
from dataclasses import asdict
from typing import Dict

import bbg_settings
from bbg_helpers import helper_aws_step
from bbg_helpers.helper_dataclass import BbgFiles, DecodeLambdaParameters
from bbg_src.files_to_decode_lambda.gpg_file_decode import BBGGPGHelper
from bbg_src.files_to_decode_lambda.select_files_for_ingest import SelectFileForIngest

from shared.shared_src.s3.s3_helper import S3Helper

log_level = bbg_settings.LOG_LEVEL
boto_log_level = bbg_settings.BOTO_LOG_LEVEL
log = logging.getLogger()


class BBGFileDecode:
    def __init__(self, event):
        self._event = event
        self._lambda_parameters = self._populate_lambda_parameters(event=self._event)
        self._aws_step = None
        self._gpg_helper = BBGGPGHelper(client_name=self._lambda_parameters.client_name)
        self._s3_obj = S3Helper(client_name=self._lambda_parameters.client_name, ingest_type="bbg")

    def _populate_lambda_parameters(self, event: Dict) -> DecodeLambdaParameters:
        lambda_parameters: DecodeLambdaParameters = DecodeLambdaParameters(**event)
        if "bbg_files" in event:
            bbg_params: BbgFiles = BbgFiles(**event["bbg_files"])
            lambda_parameters.bbg_files = bbg_params
        return lambda_parameters

    def _file_needs_processing(self, file_extension) -> bool:
        # If file extension is .gpg then file does need to be decoded
        file_needs_processing = False
        if file_extension == ".gpg":
            return True
        return file_needs_processing

    def files_to_decode(self):
        self._aws_step = helper_aws_step.AWSStepHelper(
            files_to_process=self._lambda_parameters.files_downloaded,
            files_already_processed=self._lambda_parameters.files_decoded,
        )

        if self._file_needs_processing(self._aws_step.file_extension):
            dst_file_name = self._aws_step.file_decoded.replace("downloaded", "decoded")  # shouldn't be hard coded
            self._gpg_helper.decode_file(decode_file_name=self._aws_step.file, decoded_file_name=dst_file_name)
            self._aws_step.processed_file(new_file_name=self._gpg_helper.decodedFileName)

            # Populate the bbg_files
            create_bbg_files_obj: SelectFileForIngest = SelectFileForIngest(
                full_file_path=dst_file_name, bbg_files_part=self._lambda_parameters.bbg_files
            )
            self._lambda_parameters.bbg_files = create_bbg_files_obj.generate_bbg_path()
        else:
            # don't decode, copy file from downloaded to decoded bucket
            src_key = self._aws_step.file
            dst_key = self._aws_step.file
            self._aws_step.processed_file(new_file_name=dst_key)

            try:
                self._s3_obj.copy_file_between_folders(src_key=src_key, dst_key=dst_key)
            except Exception as ex:
                err_msg = f"Failed to Copy File from {src_key} to {dst_key}. Error{ex}"
                log.error(err_msg)
                self._lambda_parameters.error = True
                self._lambda_parameters.error_msg = err_msg
                pass

        self._lambda_parameters.files_decoded = self._aws_step.output_files_processed
        self._lambda_parameters.files_downloaded = self._aws_step.output_files_to_process
        self._lambda_parameters.has_files = self._aws_step.more_to_process

        return asdict(self._lambda_parameters)
