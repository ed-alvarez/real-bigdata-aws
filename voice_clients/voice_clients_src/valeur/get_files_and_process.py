import logging
from typing import Dict, List, Tuple

from voice_clients_src.valeur import valeur_settings

from shared.shared_src.gpg.gpg_decode import GPGHelper
from shared.shared_src.helper_aws_parameters import AWS_Key_Parameters
from shared.shared_src.s3.s3_helper import S3Helper
from shared.shared_src.sftp.sftp_client import SFTPClient
from shared.shared_src.sftp.sftp_connection import SFTPConnection
from shared.shared_src.sftp.ssh_dataclass import ssh_server_creds

log = logging.getLogger()


class IterateDateList:
    def __init__(self, date_list: List, client: str):
        self._client: str = client
        self._date_list: List = date_list

    def process_list(self) -> List:
        date_list: List = self._date_list
        sftp_client: SFTPClient = self._setup_sftp_connection(client=self._client)
        s3_client: S3Helper = S3Helper(client_name=self._client, ingest_type=valeur_settings.INGEST_TYPE)
        gpg_client: GPGHelper = GPGHelper(
            client_name=self._client, passphrase_key=valeur_settings.PGP_PASSPHRASE_KEY, pem_file_key=valeur_settings.PGP_PEMFILE_KEY
        )

        for dt_day in date_list:
            day_list_of_remote_files = self._get_day_list_of_remote_files(date=dt_day, sftp_client=sftp_client)
            result: Tuple = self._decode_and_copy_remote_to_s3(
                list_of_files=day_list_of_remote_files, sftp_client=sftp_client, s3_client=s3_client, gpg_client=gpg_client
            )
            return result[0]

    def _get_day_list_of_remote_files(self, date: str, sftp_client: SFTPClient) -> List[str]:
        list_of_files: List = sftp_client.list_files_in_directory(file_prefix=date)
        return list_of_files

    def _is_copied(self, response: Dict) -> bool:
        is_copied: bool = False
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            is_copied: bool = True
        return is_copied

    def _is_encrypted_file(self, file_name: str) -> bool:
        is_encrypted_file: bool = False
        if file_name.split(".")[-1] == "gpg":
            log.debug(f"{file_name} is an encrypted file")
            is_encrypted_file = True
        else:
            log.debug(f"{file_name} is NOT an encrypted file")
        return is_encrypted_file

    def _is_audio_file(self, file_name: str) -> bool:
        is_audio_file: bool = False
        if file_name.split(".")[-1] == "wav":
            log.debug(f"{file_name} is an audio file")
            is_audio_file = True
        else:
            log.debug(f"{file_name} is NOT an audio file")
        return is_audio_file

    def _decode_and_copy_remote_to_s3(
        self, list_of_files: List, sftp_client: SFTPClient, s3_client: S3Helper, gpg_client: GPGHelper
    ) -> Tuple[List, List, List]:
        list_of_audio_files: List = []
        list_of_copied_files: List = []
        list_of_failed_to_copy_files: List = []
        for file in list_of_files:
            if self._is_encrypted_file(file_name=file):
                file_content: bytes = sftp_client.get_sftp_file(ftp_file_path=file)
                decoded_content: bytes = self._decode_file_content(file_content=file_content, gpg_client=gpg_client)
                s3_file_key = self._generate_s3_file_key(file_name=file, s3_client=s3_client)
                result = s3_client.write_file_to_s3(file_key=s3_file_key, file_content=decoded_content)
                if self._is_copied(response=result):
                    list_of_copied_files.append(s3_file_key)
                    if self._is_audio_file(file_name=s3_file_key):
                        list_of_audio_files.append(s3_file_key)
                else:
                    list_of_failed_to_copy_files.append(file)
        return list_of_audio_files, list_of_copied_files, list_of_failed_to_copy_files

    def _generate_s3_file(self, file_name: str) -> str:
        s3_raw_file: str = file_name.split("_")[1]
        s3_file: str = ".".join(s3_raw_file.split(".")[:-1])
        return s3_file

    def _generate_s3_date_folder(self, file_name: str) -> str:
        s3_raw_date_folder: str = file_name.split("-")[0]
        s3_date_folder: str = f"{s3_raw_date_folder[0:4]}-{s3_raw_date_folder[4:6]}-{s3_raw_date_folder[6:8]}"
        return s3_date_folder

    def _generate_s3_file_key(self, file_name: str, s3_client: S3Helper) -> str:
        # original file
        # 20210922-151637_1632316597.19842.json.gpg
        s3_file: str = self._generate_s3_file(file_name=file_name)
        s3_date_folder: str = self._generate_s3_date_folder(file_name=file_name)
        s3_base_path: str = s3_client._generate_base_path(base_date=s3_date_folder)
        s3_file_key: str = s3_client._generate_file_key(base_path=s3_base_path, file_name=s3_file)
        return s3_file_key

    def _decode_file_content(self, file_content: bytes, gpg_client: GPGHelper) -> bytes:
        decoded_content: bytes = gpg_client.decode_file(file_content)
        return decoded_content

    def _populate_ssh_creds(self, client: str) -> ssh_server_creds:
        """aws_parameter = AWS_Key_Parameters()
        server_creds: ssh_server_creds = ssh_server_creds()
        server_creds.client_name = client
        server_creds.sftp_host = aws_parameter.get_parameter_value(item_key=valeur_settings.SSM_SFTP_HOST_KEY,
                                                                   client_name=client)
        server_creds.sftp_port = aws_parameter.get_parameter_value(item_key=valeur_settings.SSM_SFTP_PORT_KEY,
                                                                   client_name=client)
        server_creds.ssm_account_id = aws_parameter.get_parameter_value(
            item_key=valeur_settings.SSM_SFTP_ACCOUNT_ID_KEY,
            client_name=client)
        server_creds.ssm_account_password = aws_parameter.get_parameter_value(
            item_key=valeur_settings.SSM_SFTP_ACCOUNT_PASSWORD_KEY,
            client_name=client)
        server_creds.ssm_key_file = aws_parameter.get_parameter_value(item_key=valeur_settings.SSM_SFTP_KEY_KEY,
                                                                      client_name=client)
        server_creds.ssm_key_passcode = aws_parameter.get_parameter_value(
            item_key=valeur_settings.SSM_SFTP_KEY_PASSCODE_KEY,
            client_name=client)
        return server_creds"""

        aws_parameter = AWS_Key_Parameters()
        server_creds: ssh_server_creds = ssh_server_creds()
        server_creds.client_name = client
        server_creds.sftp_host = aws_parameter.get_parameter_value(item_key=valeur_settings.SSM_SFTP_HOST_KEY, client_name=client)
        server_creds.sftp_port = aws_parameter.get_parameter_value(item_key=valeur_settings.SSM_SFTP_PORT_KEY, client_name=client)
        server_creds.ssm_account_id = aws_parameter.get_parameter_value(
            item_key=valeur_settings.SSM_SFTP_ACCOUNT_ID_KEY, client_name=client
        )
        server_creds.ssm_account_password = valeur_settings.SSM_SFTP_ACCOUNT_PASSWORD_KEY
        server_creds.ssm_key_file = valeur_settings.SSM_SFTP_KEY_KEY
        server_creds.ssm_key_passcode = valeur_settings.SSM_SFTP_KEY_PASSCODE_KEY
        return server_creds

    def _setup_sftp_connection(self, client: str) -> SFTPClient:
        log.info({f"Populate Server Creds"})
        server_creds = self._populate_ssh_creds(client=client)
        log.info({f"Create SFTP Connection"})
        ssh_connection: SFTPConnection = SFTPConnection(ssh_server_credentials=server_creds)
        ssh_connection.connect()
        sftp_client: SFTPClient = SFTPClient(sftp_connection=ssh_connection)
        return sftp_client
