from typing import Dict

import pytest
from bbg_helpers.helper_dataclass import BbgFiles
from bbg_src.files_to_decode_lambda.files_to_decode import SelectFileForIngest


class TestPaths:
    @pytest.fixture()
    def file_ingest_obj(self) -> SelectFileForIngest:
        yield SelectFileForIngest(full_file_path="", bbg_files_part=BbgFiles())

    bbg_files_ib_normal_tar: BbgFiles = BbgFiles()
    bbg_files_ib_normal_tar.IB_ATT_file_name = "dev.todo.bbg/2021-02-05/decoded/f908067.att.210205.tar.gz"

    bbg_out_files_ib_normal_tar: BbgFiles = BbgFiles()
    bbg_out_files_ib_normal_tar.IB_ATT_file_name = "dev.todo.bbg/2021-02-05/decoded/f908067.att.210205.tar.gz"

    test_1 = {
        "full_file_path": "dev.todo.bbg/2021-02-05/decoded/f908067.ib19.att.210205.tar.gz",
        "bbg_files_path": bbg_files_ib_normal_tar,
        "isNewArchiveFormat": False,
    }

    bbg_files_msg_normal_tar: BbgFiles = BbgFiles()
    bbg_files_msg_normal_tar.MSG_ATT_file_name = "dev.todo.bbg/2021-02-05/decoded/f908067.att.210205.tar.gz"

    bbg_out_files_msg_normal_tar: BbgFiles = BbgFiles()
    bbg_out_files_msg_normal_tar.MSG_ATT_file_name = "dev.todo.bbg/2021-02-05/decoded/f908067.att.210205.tar.gz"

    test_2 = {
        "full_file_path": "dev.todo.bbg/2021-02-05/decoded/f908067.ib19.att.210205.tar.gz",
        "bbg_files_path": bbg_files_msg_normal_tar,
        "isNewArchiveFormat": False,
    }

    bbg_files_ib_new_tar: BbgFiles = BbgFiles()
    bbg_files_ib_new_tar.IB_ATT_file_name = "dev.todo.bbg/2021-02-05/decoded/f908067.att.210205.tar.gz"

    bbg_out_files_ib_new_tar: BbgFiles = BbgFiles()
    bbg_out_files_ib_new_tar.IB_ATT_file_name = "dev.todo.bbg/2021-02-05/decoded/f908067.att.210205.tar.gz"

    test_3 = {
        "full_file_path": "dev.todo.bbg/2021-02-05/decoded/f908067.ib19.att.210205.tar.gz",
        "bbg_files_path": bbg_files_ib_new_tar,
        "isNewArchiveFormat": True,
    }

    bbg_files_msg_new_tar: BbgFiles = BbgFiles()
    bbg_files_msg_new_tar.MSG_ATT_file_name = "dev.todo.bbg/2021-02-05/decoded/f908067.att.210205.tar.gz"

    bbg_out_files_msg_new_tar: BbgFiles = BbgFiles()
    bbg_out_files_msg_new_tar.MSG_ATT_file_name = "dev.todo.bbg/2021-02-05/decoded/f908067.msg.att.210205.tar.gz"

    test_4 = {
        "full_file_path": "dev.todo.bbg/2021-02-05/decoded/f908067.msg.att.210205.tar.gz",
        "bbg_files_path": bbg_files_msg_new_tar,
        "isNewArchiveFormat": True,
    }

    CASES = [(test_2, bbg_out_files_msg_normal_tar), (test_4, bbg_out_files_msg_new_tar)]

    @pytest.mark.parametrize("input, expected", CASES)
    def test_populate_bbg_path_msg(self, input, expected, file_ingest_obj):
        response: BbgFiles = file_ingest_obj._populate_bbg_path(**input)
        assert response.IB_ATT_file_name == expected.IB_ATT_file_name

    CASES = [
        (test_1, bbg_out_files_ib_normal_tar),
        (test_3, bbg_out_files_ib_new_tar),
    ]

    @pytest.mark.parametrize("input, expected", CASES)
    def test_populate_bbg_path_ib(self, input, expected, file_ingest_obj):
        response: BbgFiles = file_ingest_obj._populate_bbg_path(**input)
        assert response.MSG_ATT_file_name == expected.MSG_ATT_file_name


class TestIBOnlyFile:
    input_event_1: BbgFiles = BbgFiles()

    input_file_name_1: str = "todo.bbg/2021-06-10/decoded/f886973.ib19.210610.xml"
    output_event_1: BbgFiles = BbgFiles(
        **{
            "MSG_XML_to_process": False,
            "MSG_file_name": "",
            "MSG_ATT_file_name": "",
            "MSG_XML_record_number": 0,
            "IB_XML_to_process": True,
            "IB_file_name": "todo.bbg/2021-06-10/decoded/f886973.ib19.210610.xml",
            "IB_ATT_file_name": "",
            "IB_XML_record_number": 0,
        }
    )

    input_file_name_2: str = "todo.bbg/2021-06-10/decoded/f886973.ib19.att.210610.tar.gz"

    output_event_2: BbgFiles = BbgFiles(
        **{
            "MSG_XML_to_process": False,
            "MSG_file_name": "",
            "MSG_ATT_file_name": "",
            "MSG_XML_record_number": 0,
            "IB_XML_to_process": True,
            "IB_file_name": "todo.bbg/2021-06-10/decoded/f886973.ib19.210610.xml",
            "IB_ATT_file_name": "todo.bbg/2021-06-10/decoded/f886973.ib19.att.210610.tar.gz",
            "IB_XML_record_number": 0,
        }
    )

    CASES = [
        (input_event_1, input_file_name_1, output_event_1),
        (output_event_1, input_file_name_2, output_event_2),
    ]

    @pytest.mark.parametrize("input_event, input_file, expected_event", CASES)
    def test_new_bbg_att_file(self, input_event, input_file, expected_event):
        select_file_obj: SelectFileForIngest = SelectFileForIngest(full_file_path=input_file, bbg_files_part=input_event)
        result: BbgFiles = select_file_obj.generate_bbg_path()
        assert result == expected_event


class TestNormalFiles:
    file_list_0 = [
        "todo.bbg/2021-05-14/decoded/f886973.ib.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.msg.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.att.210514.tar.gz",
        "todo.bbg/2021-05-14/decoded/f886973.msg.att.210514.tar.gz",
        "todo.bbg/2021-05-14/decoded/f886973.dscl.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.ib19.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.ib19.att.210514.tar.gz",
    ]

    file_list_1 = [
        "todo.bbg/2021-05-14/decoded/f886973.ib19.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.ib19.att.210514.tar.gz",
        "todo.bbg/2021-05-14/decoded/f886973.ib.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.msg.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.att.210514.tar.gz",
        "todo.bbg/2021-05-14/decoded/f886973.msg.att.210514.tar.gz",
        "todo.bbg/2021-05-14/decoded/f886973.dscl.210514.xml",
    ]

    file_list_2 = [
        "todo.bbg/2021-05-14/decoded/f886973.ib19.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.ib19.att.210514.tar.gz",
        "todo.bbg/2021-05-14/decoded/f886973.ib.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.msg.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.msg.att.210514.tar.gz",
        "todo.bbg/2021-05-14/decoded/f886973.dscl.210514.xml",
    ]

    file_list_3 = [
        "todo.bbg/2021-05-14/decoded/f886973.ib19.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.ib19.att.210514.tar.gz",
        "todo.bbg/2021-05-14/decoded/f886973.msg.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.msg.att.210514.tar.gz",
        "todo.bbg/2021-05-14/decoded/f886973.dscl.210514.xml",
    ]

    file_list_4 = [
        "todo.bbg/2021-05-14/decoded/f886973.ib.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.msg.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.att.210514.tar.gz",
        "todo.bbg/2021-05-14/decoded/f886973.dscl.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.ib19.210514.xml",
        "todo.bbg/2021-05-14/decoded/f886973.ib19.att.210514.tar.gz",
    ]

    file_list_5 = [
        "todo.bbg/2021-06-11/decoded/f886973.ib19.210611.xml",
        "todo.bbg/2021-06-11/decoded/f886973.ib19.att.210611.tar.gz",
    ]

    expected_result_0 = BbgFiles(
        **{
            "MSG_XML_to_process": True,
            "MSG_file_name": "todo.bbg/2021-05-14/decoded/f886973.msg.210514.xml",
            "MSG_ATT_file_name": "todo.bbg/2021-05-14/decoded/f886973.msg.att.210514.tar.gz",
            "MSG_XML_record_number": 0,
            "IB_XML_to_process": True,
            "IB_file_name": "todo.bbg/2021-05-14/decoded/f886973.ib19.210514.xml",
            "IB_ATT_file_name": "todo.bbg/2021-05-14/decoded/f886973.ib19.att.210514.tar.gz",
            "IB_XML_record_number": 0,
        }
    )

    expected_result_1 = BbgFiles(
        **{
            "MSG_XML_to_process": True,
            "MSG_file_name": "todo.bbg/2021-05-14/decoded/f886973.msg.210514.xml",
            "MSG_ATT_file_name": "todo.bbg/2021-05-14/decoded/f886973.att.210514.tar.gz",
            "MSG_XML_record_number": 0,
            "IB_XML_to_process": True,
            "IB_file_name": "todo.bbg/2021-05-14/decoded/f886973.ib19.210514.xml",
            "IB_ATT_file_name": "todo.bbg/2021-05-14/decoded/f886973.ib19.att.210514.tar.gz",
            "IB_XML_record_number": 0,
        }
    )

    expected_result_2 = BbgFiles(
        **{
            "MSG_XML_to_process": False,
            "MSG_file_name": "",
            "MSG_ATT_file_name": "",
            "MSG_XML_record_number": 0,
            "IB_XML_to_process": True,
            "IB_file_name": "todo.bbg/2021-06-11/decoded/f886973.ib19.210611.xml",
            "IB_ATT_file_name": "todo.bbg/2021-06-11/decoded/f886973.ib19.att.210611.tar.gz",
            "IB_XML_record_number": 0,
        }
    )

    CASES = [
        (file_list_0, expected_result_0),
        (file_list_1, expected_result_0),
        (file_list_2, expected_result_0),
        (file_list_3, expected_result_0),
        (file_list_4, expected_result_1),
        (file_list_5, expected_result_2),
    ]

    @pytest.mark.parametrize("input_file_list, expected_event", CASES)
    def test_new_files_chosen_over_old(self, input_file_list, expected_event):
        working_bbg_event = BbgFiles()
        for file in input_file_list:
            files_obj: SelectFileForIngest = SelectFileForIngest(full_file_path=file, bbg_files_part=working_bbg_event)
            working_bbg_event = files_obj.generate_bbg_path()
        assert working_bbg_event == expected_event
