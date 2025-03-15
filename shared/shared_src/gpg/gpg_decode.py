import logging

from pgpy import PGPKey, PGPMessage

from shared.shared_src.helper_aws_parameters import AWS_Key_Parameters

log = logging.getLogger()


class GPGHelper:
    def __init__(self, client_name: str, pem_file_key: str, passphrase_key: str) -> None:
        self._client_name: str = client_name
        self._aws_parameters: AWS_Key_Parameters = AWS_Key_Parameters(client_name=self._client_name)
        self._pem_file_key: str = pem_file_key
        self._passphrase_key: str = passphrase_key

    def decode_file(self, file_blob) -> bytes:
        pgp_key: str = self._aws_parameters.get_parameter_value(item_key=self._pem_file_key)
        pgp_passphrase: str = self._aws_parameters.get_parameter_value(item_key=self._passphrase_key)

        key, _ = PGPKey.from_blob(pgp_key)
        message_from_blob: PGPMessage = PGPMessage.from_blob(file_blob)

        with key.unlock(pgp_passphrase):
            file_decrypted_content = key.decrypt(message_from_blob)

        if not file_decrypted_content.message:
            raise KeyError("No Data Decrypted")

        log.info("Decryption Sucessful")
        binary_file_contents: bytes = bytes(file_decrypted_content.message)
        return binary_file_contents
