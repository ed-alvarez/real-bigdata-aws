"""
SFTP client class
"""
import io
import logging

import bbg_settings
import paramiko
import requests  # requests library doesn't come by default in lambda

from shared.shared_src.helper_aws_parameters import AWS_Key_Parameters

log_level = bbg_settings.LOG_LEVEL
log = logging.getLogger()


class SFTPConnection:
    def __init__(self, client_name, client_id):
        self.STORE_TYPE = bbg_settings.STORE_TYPE
        self.SSH_HOST = bbg_settings.SSH_HOST
        self.SSH_PORT = bbg_settings.SSH_PORT
        self.SSH_FILE_KEY = bbg_settings.SSH_FILE_KEY
        self.SSH_PASSPHRASE_KEY = bbg_settings.SSH_PASSPHRASE_KEY
        self.SSH_PASSWORD_KEY = bbg_settings.SSH_PASSWORD_KEY
        self.client_name = client_name
        self.client_id = client_id
        self.ssh = paramiko.SSHClient()
        self.sftp_client = None
        self.ip_address = requests.get("http://checkip.amazonaws.com").text.rstrip()
        self._client_parameters = None
        self._client_connection = None
        self._connect()

    def client_connection(self):
        ssm_parameter = AWS_Key_Parameters(client_name=self.client_name)

        log.info("Searching for ssh password")
        bbg_ssh_password = ssm_parameter.get_parameter_value(item_key=self.SSH_PASSWORD_KEY)
        if bbg_ssh_password:
            log.info("Password found, connecting....")
            try:
                return self._connect_pass(bbg_ssh_password)
            except KeyError as ex:
                log.warning("Cannot connect with password")
                pass

        log.info("Searching for Key & Passphrase")
        bbg_ssh_key = ssm_parameter.get_parameter_value(item_key=self.SSH_FILE_KEY)
        bbg_ssh_passphrase = ssm_parameter.get_parameter_value(item_key=self.SSH_PASSPHRASE_KEY)
        if bbg_ssh_passphrase and bbg_ssh_key:
            log.info("Key & Passphrase found, connecting...")
            try:
                return self._connect_key(bbg_ssh_key, bbg_ssh_passphrase)
            except KeyError as ex:
                err_msg = "ERROR: No matching Credentials found to enable login from this IP address"
                log.error(err_msg)
                raise KeyError(err_msg)

    def _connect_key(self, bbg_ssh_key, bbg_ssh_passphrase):
        str_key = io.StringIO(bbg_ssh_key)
        pkey = paramiko.RSAKey.from_private_key(str_key, password=bbg_ssh_passphrase)
        log.debug('{"bbg_id" : "%s"}' % self.client_id)
        log.debug('{"bbg_ssh_key" : "%s"}' % bbg_ssh_key)
        try:
            self.ssh.connect(
                hostname=self.SSH_HOST,
                port=self.SSH_PORT,
                username=self.client_id,
                pkey=pkey,
                look_for_keys=False,
            )
        except Exception as ex:
            if type(ex) in [paramiko.AuthenticationException, paramiko.ssh_exception.NoValidConnectionsError]:
                if log_level == "DEBUG":
                    log.error(
                        f"Connect Error {ex}. From {self.ip_address} to {self.SSH_HOST}:{self.SSH_PORT} for "
                        f"user = {self.client_id} pkey = {bbg_ssh_key}"
                    )
                    raise ex
                else:
                    log.error(f"Connect Error {ex}")
                    raise ex
            else:
                log.error(f"General Error {ex}")
                raise ex

    def _connect_pass(self, bbg_ssh_password):
        log.debug('{"bbg_id" : "%s"}' % self.client_id)
        log.debug('{"bbg_ssh_password" : "%s"}' % bbg_ssh_password)

        try:
            self.ssh.connect(hostname=self.SSH_HOST, port=self.SSH_PORT, username=self.client_id, password=bbg_ssh_password)
        except (paramiko.AuthenticationException, paramiko.ssh_exception.NoValidConnectionsError) as ex:
            if log_level == "DEBUG":
                log.error(
                    f"Connect Error {ex}. From {self.ip_address} to {self.SSH_HOST}:{self.SSH_PORT} for "
                    f"user = {self.client_id} password = {bbg_ssh_password}"
                )
                raise ex
            else:
                log.error(f"Connect Error {ex}")
                raise ex

    def _connect(self):
        # self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

        log.debug('{"public_ip_address" : "%s"}', self.ip_address)
        log.debug('{"Host" : "%s"}' % self.SSH_HOST)
        log.debug('{"Port" : "%s"}' % self.SSH_PORT)

        try:
            self.client_connection()

        except (paramiko.AuthenticationException, paramiko.ssh_exception.NoValidConnectionsError) as ex:
            log.error(f"No Common Connection Types")
            self.ssh.close()
            raise ex

        self.sftp_client = self.ssh.open_sftp()
        log.debug('{"SFTP Client" : "%s"}' % self.sftp_client)


if __name__ == "__main__":
    test_sftp = SFTPConnection(client_id="mc913915589", client_name="melqart")
    print(test_sftp)
