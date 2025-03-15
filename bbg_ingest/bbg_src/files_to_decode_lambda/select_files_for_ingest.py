import logging
from os import path
from typing import List

from bbg_helpers.helper_dataclass import BbgFiles

log = logging.getLogger()


class SelectFileForIngest:
    def __init__(self, full_file_path: str, bbg_files_part: BbgFiles):
        self._full_file_path: str = full_file_path
        self._file_name: str = path.basename(self._full_file_path)
        self._bbg_files_part: BbgFiles = bbg_files_part
        self.MSG_file_found: bool = False
        self.IB_file_found: bool = False
        self.IB19_file_found: bool = False
        self.ATT_file_found: bool = False
        self.DSCL_file_found: bool = False
        self._new_bbg_file_format: bool = False

    def _get_file_parts(self, file_name: str) -> List:
        return file_name.split(".")

    def _set_new_bloomberg_file_format(self, file_name: str) -> None:
        """
        the old att file format is f886973.att.210514.tar.gz so item 2 is the date
        the new att file format is f886973.ib19.att.210514.tar.gz and f886973.msg.att.210514.tar.gz so item 2 is att
        """
        if self._get_file_parts(file_name=file_name)[2] == "att":
            self._new_bbg_file_format = True

    def _get_type_of_file(self, file_name: str) -> str:
        file_type = self._get_file_parts(file_name=file_name)[1]
        return file_type

    def _set_type_of_file(self, file_type: str) -> None:
        if file_type == "msg":
            self.MSG_file_found = True

        elif file_type == "ib":
            self.IB_file_found = True

        elif file_type == "ib19":
            self.IB19_file_found = True

        elif file_type == "att":
            self.ATT_file_found = True

        elif file_type == "dscl":
            self.DSCL_file_found = True

    def _populate_bbg_path(self, bbg_files_path: BbgFiles, full_file_path: str, isNewArchiveFormat: bool) -> BbgFiles:
        new_bbg_files_path: bbg_files_path = bbg_files_path
        """
        Populate the att file name to be the same thing for both IB & MSG if it is not already populated.
        This means that if the file order places f886973.msg.att.210514.tar.gz before f886973.att.210514.tar.gz
        the the att path will not be populated
        """
        if self.ATT_file_found:
            if not bbg_files_path.MSG_ATT_file_name:
                new_bbg_files_path.MSG_ATT_file_name = full_file_path
            if not bbg_files_path.IB_ATT_file_name:
                new_bbg_files_path.IB_ATT_file_name = full_file_path

        elif self.MSG_file_found:
            if isNewArchiveFormat:
                new_bbg_files_path.MSG_ATT_file_name = full_file_path
            else:
                new_bbg_files_path.MSG_XML_to_process = True
                new_bbg_files_path.MSG_file_name = full_file_path
                new_bbg_files_path.MSG_XML_record_number = 0
                new_bbg_files_path.MSG_json_file_number = 0

        elif self.IB_file_found:
            if isNewArchiveFormat:
                new_bbg_files_path.IB_ATT_file_name = full_file_path
            else:
                new_bbg_files_path.IB_XML_to_process = True
                if not new_bbg_files_path.IB_file_name:
                    new_bbg_files_path.IB_file_name = full_file_path
                new_bbg_files_path.IB_XML_record_number = 0
                new_bbg_files_path.IB_conversation_item = 0

        elif self.IB19_file_found:
            if isNewArchiveFormat:
                new_bbg_files_path.IB_ATT_file_name = full_file_path
            else:
                new_bbg_files_path.IB_XML_to_process = True
                new_bbg_files_path.IB_file_name = full_file_path
                new_bbg_files_path.IB_XML_record_number = 0
                new_bbg_files_path.IB_conversation_item = 0

        return new_bbg_files_path

    def generate_bbg_path(self) -> BbgFiles:
        file_type: str = self._get_type_of_file(file_name=self._file_name)
        self._set_type_of_file(file_type=file_type)
        self._set_new_bloomberg_file_format(file_name=self._file_name)
        new_bbg_file_part: BbgFiles = self._populate_bbg_path(
            bbg_files_path=self._bbg_files_part,
            full_file_path=self._full_file_path,
            isNewArchiveFormat=self._new_bbg_file_format,
        )
        return new_bbg_file_part
