import io
from pathlib import Path
from typing import Dict

import pytest
from paramiko import AUTH_FAILED, AUTH_SUCCESSFUL, RSAKey, SFTPClient

from shared.shared_src.sftp.sftp_connection import SFTPConnection
from shared.shared_src.sftp.ssh_dataclass import ssh_server_creds

BASE_DIR = Path(__file__).resolve().parent.resolve().parent.resolve()

ssh_server_creds.client_name = "testing"
ssh_server_creds.sftp_host = "127.0.0.1"
ssh_server_creds.sftp_port = 2223
ssh_server_creds.ssm_account_id = "test-account"
ssh_server_creds.ssm_key_file = "public_key"
ssh_server_creds.ssm_key_passcode = "public_key_password"
ssh_server_creds.ssm_account_password = "password"


@pytest.mark.skip(reason="no way of currently testing this")
class TestFunction:
    def test_set_connection_params(self):
        test_obj: SFTPConnection = SFTPConnection(ssh_server_credentials=ssh_server_creds)
        result = test_obj._set_connection_params(ssh_server_creds=ssh_server_creds, password="P@ssword")
        assert "pkey" not in result.keys()

    test_param: Dict = {
        "hostname": ssh_server_creds.sftp_host,
        "port": ssh_server_creds.sftp_port,
        "username": ssh_server_creds.ssm_account_id,
        "look_for_keys": False,
    }

    test1 = test_param.copy()
    test1["password"] = "P@ssword"

    with open(f"{BASE_DIR}/fixtures/sftp/sftpkey") as f:
        priv_key_contents = f.read()
    str_key = io.StringIO(priv_key_contents)
    ssh_passphrase = ""
    pkey = RSAKey.from_private_key(str_key, password=ssh_passphrase)

    test2 = test_param.copy()
    test2["pkey"] = pkey

    CASES = [(test1, True), (test2, True)]

    @pytest.mark.parametrize("dummy_tcp_server", [AUTH_SUCCESSFUL], indirect=["dummy_tcp_server"])
    @pytest.mark.parametrize("test_params, expected", CASES)
    def test_sucess_connect_with_param(self, test_params, expected, dummy_tcp_server):
        with dummy_tcp_server:
            test_obj: SFTPConnection = SFTPConnection(ssh_server_credentials=ssh_server_creds)
            test_obj._connect_with_param(connect_param=test_params)
            result = test_obj.ssh.get_transport()
            assert result.authenticated is expected

    CASES = [(test1, False), (test2, False)]

    @pytest.mark.parametrize("dummy_tcp_server", [AUTH_FAILED], indirect=["dummy_tcp_server"])
    @pytest.mark.parametrize("test_params, expected", CASES)
    def test_fail_connect_with_param(self, test_params, expected, dummy_tcp_server):
        with dummy_tcp_server:
            test_obj: SFTPConnection = SFTPConnection(ssh_server_credentials=ssh_server_creds)
            test_obj._connect_with_param(connect_param=test_params)
            result = test_obj.ssh.get_transport()
            assert result.authenticated is expected

    @pytest.mark.parametrize("dummy_tcp_server", [AUTH_SUCCESSFUL], indirect=["dummy_tcp_server"])
    def test_sucess_connect(self, dummy_tcp_server, ssm_shared_sftp_setup):
        with ssm_shared_sftp_setup:
            with dummy_tcp_server:
                test_obj: SFTPConnection = SFTPConnection(ssh_server_credentials=ssh_server_creds)
                test_obj.connect()
                assert type(test_obj.sftp_client) is SFTPClient
