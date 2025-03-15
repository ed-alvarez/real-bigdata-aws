import io
from pathlib import Path
from typing import Dict

import pytest

from shared.shared_src.sftp.sftp_client import SFTPClient as IPS_SFTPClient
from shared.shared_src.sftp.sftp_connection import SFTPConnection
from shared.shared_src.sftp.ssh_dataclass import ssh_server_creds

BASE_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture()
def ssh_connection(ssm_shared_sftp_setup, dummy_tcp_server):
    ssh_server_creds.client_name = "testing"
    ssh_server_creds.sftp_host = "127.0.0.1"
    ssh_server_creds.sftp_port = 2222
    ssh_server_creds.ssm_account_id = "test-account"
    ssh_server_creds.ssm_key_file = "public_key"
    ssh_server_creds.ssm_key_passcode = "public_key_password"
    ssh_server_creds.ssm_account_password = "password"
    with ssm_shared_sftp_setup:
        ssh_connection: SFTPConnection = SFTPConnection(ssh_server_credentials=ssh_server_creds)
        ssh_connection.connect()

    yield ssh_connection


@pytest.mark.skip(reason="no way of currently testing this")
class TestSFTPClient:
    def test_get_file_blob(self, ssh_connection, dummy_tcp_server):
        with dummy_tcp_server:
            test_obj = IPS_SFTPClient(sftp_connection=ssh_connection)
            file = "20210922-151637_1632316597.19842.json.gpg"
            result = test_obj.get_sftp_file(ftp_file_path=file)
        assert type(result) is bytes

    def test_get_wrong_file_blob(self, ssh_connection, dummy_tcp_server):
        with pytest.raises(Exception) as execinfo:
            with dummy_tcp_server:
                test_obj = IPS_SFTPClient(sftp_connection=ssh_connection)
                file = "does_not_exist.txt"
                result = test_obj.get_sftp_file(ftp_file_path=file)
        assert execinfo.value.args[1] == "No such file"

    def test_list_directory(self, ssh_connection, dummy_tcp_server):
        with dummy_tcp_server:
            test_obj = IPS_SFTPClient(sftp_connection=ssh_connection)
            result = test_obj.list_files_in_directory()
            assert "20210922-151637_1632316597.19842.json.gpg" in result
