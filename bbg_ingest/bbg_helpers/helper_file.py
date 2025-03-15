"""
Class to deal with S3 File paths/names etc etd
"""

import logging
import os

log = logging.getLogger()


class FileHelper:
    def __init__(self, file):
        self.file = file
        self.file_key = None

        self.file_directory, self.file_name = os.path.split(self.file)
        log.debug('{"file_directory" : "%s"}', self.file_directory)
        log.debug('{"file_name" : "%s"}', self.file_name)
        var = os.environ.get("AWS_EXECUTION_ENV")
        if var is None:
            self.tmp_file = os.path.join("/tmp", self.file_name)
        else:
            self.tmp_file = os.path.join("/tmp", self.file_name)

        log.debug('{"tmp_file" : "%s"}', self.tmp_file)

        self.file_part, self.file_extension = os.path.splitext(self.file_name)

    def __str__(self):
        return self.file


class BBGFileHelper(FileHelper):
    def __init__(self, file):
        super().__init__(file=file)
        self.MSG_file_found = False
        self.IB_file_found = False
        self.ATT_file_found = False
        self.DSCL_file_found = False
        self.stream_name = None
        self.s3_base_path = None

        self.new_format_archive = False
        self.file_parts = self.file_name.split(".")
        self.bloomberg_account = self.file_parts[0]
        log.debug('{"bloomberg_account" : "%s"}', self.bloomberg_account)
        self.bloomberg_file_type = self.file_parts[1]
        log.debug('{"bbg_file_type" : "%s"}', self.bloomberg_file_type)
        if self.file_parts[2] == "att":
            self.new_format_archive = True
            self.bloomberg_file_date = self.file_parts[3]
            log.warning(f"NEW bbg archive format {self.file_name}")
        else:
            self.bloomberg_file_date = self.file_parts[2]
        log.debug('{"bbg_file_date" : "%s"}', self.bloomberg_file_date)

        if self.bloomberg_file_type == "msg":
            self.MSG_file_found = True

        elif self.bloomberg_file_type == "ib" or self.bloomberg_file_type == "ib19":
            self.IB_file_found = True

        elif self.bloomberg_file_type == "att":
            self.ATT_file_found = True

        elif self.bloomberg_file_type == "dscl":
            self.DSCL_file_found = True

        self.bbg_folder_date = str(
            "20"
            + str(self.bloomberg_file_date[0:2])
            + "-"
            + str(self.bloomberg_file_date[2:4])
            + "-"
            + str(self.bloomberg_file_date[4:6])
        )
        log.debug('{"bbg_folder_date" : "%s"}', self.bbg_folder_date)

        self.generate_base_path(directory="decoded")
        self.generate_file_key(self.file_name)

    def generate_base_path(self, directory=None):
        self.stream_name = "processed.bbg"
        if os.environ.get("STAGE") == "dev" or os.environ.get("AWS_EXECUTION_ENV") is None:
            self.stream_name = "dev." + self.stream_name
        self.s3_base_path = os.path.join(self.stream_name, self.bbg_folder_date, directory)
        log.debug("generate_base_path, -> self.s3_base_path, {}".format(self.s3_base_path))
        return self.s3_base_path

    def generate_file_key(self, file_name):
        self.file_key = os.path.join(self.s3_base_path, file_name)
        log.debug("generate_file_key, file_name, {}, -> self.file_key, {}".format(file_name, self.file_key))
        return self.file_key


class JSONFileHelper(BBGFileHelper):
    def __init__(self, file, message_id=None):
        super().__init__(file=file)

        if message_id or message_id == 0:
            self.json_message_id = str(message_id)
            log.debug('{"json_message_id" : "%s"}', self.json_message_id)

            self.json_tmp_file_name = self.file_part + "." + self.json_message_id + ".json"
            log.debug('{"json_tmp_file_name" : "%s"}', self.json_tmp_file_name)

        else:
            self.json_tmp_file_name = self.file_part + ".json"
            log.debug('{"json_tmp_file_name" : "%s"}', self.json_tmp_file_name)

        self.json_tmp_full_file_name = "/tmp/" + self.json_tmp_file_name
        log.debug('{"json_tmp_full_file_name" : "%s"}', self.json_tmp_full_file_name)

        self.generate_base_path(directory="json")
        self.generate_file_key(self.json_tmp_file_name)
        self.s3_json_file = self.file_key
        log.debug('{"s3_json_file" : "%s"}', self.s3_json_file)

    def __str__(self):
        return self.json_tmp_file_name
