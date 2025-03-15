import logging
import os

from bbg_helpers.helper_file import FileHelper

log = logging.getLogger()


class AWSStepHelper:
    def __init__(self, files_to_process, files_already_processed):
        self.files_to_process = files_to_process
        if files_already_processed:
            self.files_already_processed = files_already_processed
        else:
            self.files_already_processed = []

        file_obj = FileHelper(self.files_to_process[0])
        self.file = file_obj.file
        self.file_path = file_obj.file_directory
        self.file_name = file_obj.file_name
        self.file_part = file_obj.file_part
        self.file_extension = file_obj.file_extension
        self.more_to_process = False
        self.file_decoded = os.path.join(self.file_path, self.file_part)

        self.output_files_to_process = []
        self.output_files_to_process = self.files_to_process
        self.output_files_processed = []
        self.output_files_processed = self.files_already_processed

    def processed_file(self, new_file_name=None):
        self.files_to_process.pop(0)
        self.output_files_to_process = self.files_to_process
        if new_file_name:
            self.files_already_processed.append(new_file_name)
        else:
            self.files_already_processed.append(self.file)
        self.output_files_processed = self.files_already_processed
        if len(self.files_to_process) > 0:
            self.more_to_process = True


class StepMessage:
    def __init__(self, step_key=None):
        self.message = {}
        self.step_key = step_key
        self.message[self.step_key] = {}

    def create_key_value(self, **kwargs):
        for key, value in kwargs.items():
            if key not in self.message[self.step_key]:
                self.message[self.step_key][key] = []

            self.message[self.step_key][key].append(value)
