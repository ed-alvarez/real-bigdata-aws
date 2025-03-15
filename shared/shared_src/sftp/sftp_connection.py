"""
SFTP client class
"""
import io
import logging
import sys
from typing import Dict, Tuple

import paramiko
import requests  # requests library doesn't come by default in lambda

from shared.shared_src.helper_aws_parameters import AWS_Key_Parameters
from shared.shared_src.sftp.ssh_dataclass import ssh_server_creds

log = logging.getLogger()


class SFTPConnection:
    def __init__(self, ssh_server_credentials: ssh_server_creds):
        self._ssh_server_creds = ssh_server_credentials
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh_error: str = ""
        self.sftp_client = None
        self.ip_address = requests.get("https://checkip.amazonaws.com").text.rstrip()

    # self._connect()

    def _get_ssm_password(self, client_name: str, ssm_password_key: str) -> Tuple[str, str]:
        password: str = ""
        log.info("Searching for ssh password")
        ssm_parameter = AWS_Key_Parameters(client_name=client_name)
        password = ssm_parameter.get_parameter_value(item_key=ssm_password_key)
        return (password, ssm_parameter._client_name)

    def _get_ssm_ssh_key(self, client_name: str, ssm_key_file: str, ssm_key_passcode: str) -> Tuple[str, str, str]:
        ssh_key: str = ""
        ssh_passphrase: str = ""
        log.info("Searching for Key & Passphrase")
        ssm_parameter = AWS_Key_Parameters(client_name=client_name)
        ssh_key = ssm_parameter.get_parameter_value(item_key=ssm_key_file)
        ssh_passphrase = ssm_parameter.get_parameter_value(item_key=ssm_key_passcode)
        return (ssh_key, ssh_passphrase, ssm_parameter._client_name)

    def _create_client_connection(self, ssh_server_creds: ssh_server_creds) -> bool:
        is_connected: bool = False

        ssh_password, ssh_client_name = self._get_ssm_password(
            client_name=ssh_server_creds.client_name, ssm_password_key=ssh_server_creds.ssm_account_password
        )
        connection_param: Dict = {}
        if ssh_password:
            connection_param = self._set_connection_params(ssh_server_creds=ssh_server_creds, password=ssh_password)
            log.info("Password found, connecting....")

        else:
            ssh_key, ssh_passphrase, ssh_client_name = self._get_ssm_ssh_key(
                client_name=ssh_server_creds.client_name,
                ssm_key_file=ssh_server_creds.ssm_key_file,
                ssm_key_passcode=ssh_server_creds.ssm_key_passcode,
            )

            if ssh_key:
                log.info("Key found, connecting...")
                connection_param = self._set_connection_params(
                    ssh_server_creds=ssh_server_creds, ssh_key=ssh_key, ssh_passphrase=ssh_passphrase
                )
        try:
            self._connect_with_param(connect_param=connection_param)
            is_connected = True
            log.info(f"Connected with the {ssh_client_name} account")
        except KeyError as ex:
            err_msg = "ERROR: No matching Credentials found to enable login from this IP address"
            log.error(err_msg)

        return is_connected

    def _set_connection_params(
        self,
        ssh_server_creds: ssh_server_creds,
        ssh_key: str = "",
        ssh_passphrase: str = "",
        password: str = "",
    ) -> Dict:
        connect_param: Dict = {}
        connect_param["hostname"] = ssh_server_creds.sftp_host
        connect_param["port"] = ssh_server_creds.sftp_port
        connect_param["username"] = ssh_server_creds.ssm_account_id
        connect_param["look_for_keys"] = False
        if password:
            log.debug('{"password" : "%s"}' % password)
            connect_param["password"] = password
        if ssh_key:
            log.debug('{"ssh_key" : "%s"}' % ssh_key)
            str_key = io.StringIO(ssh_key)
            pkey = paramiko.RSAKey.from_private_key(str_key, password=ssh_passphrase)
            connect_param["pkey"] = pkey

        return connect_param

    def _connect_with_param(self, connect_param: Dict) -> None:
        try:
            self.ssh.connect(**connect_param)
        except paramiko.AuthenticationException as ex:
            log.exception(ex)
            self.ssh_error = paramiko.AuthenticationException
        except paramiko.ssh_exception.NoValidConnectionsError as ex:
            log.exception(ex)
            self.ssh_error = paramiko.ssh_exception.NoValidConnectionsError
        except Exception as ex:
            log.exception(ex)
            log.error(f"General Error {ex}")
            self.ssh_error = ex
        return

    def connect(self):
        # self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

        log.info('{"public_ip_address" : "%s"}', self.ip_address)
        log.info('{"Host" : "%s"}' % self._ssh_server_creds.sftp_host)
        log.info('{"Port" : "%s"}' % self._ssh_server_creds.sftp_port)

        try:
            self._create_client_connection(ssh_server_creds=self._ssh_server_creds)

        except (paramiko.AuthenticationException, paramiko.ssh_exception.NoValidConnectionsError) as ex:
            log.error("No Common Connection Types")
            self.ssh.close()
            raise ex

        self.sftp_client = self.ssh.open_sftp()
        log.debug('{"SFTP Client" : "%s"}' % self.sftp_client)

        return self.ssh
