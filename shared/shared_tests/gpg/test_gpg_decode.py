from pathlib import Path

import pytest

from shared.shared_src.gpg.gpg_decode import GPGHelper

BASE_DIR = Path(__file__).resolve().parent.parent


class TestDecodeWrapper:
    def test_decode(self, ssm_shared_gpg_setup):
        test_obj = GPGHelper(client_name="fred", passphrase_key="voice/gpgprivkeypass", pem_file_key="voice/gpgprivkey.pem")

        with open(f"{BASE_DIR}/fixtures/sftp/20210922-151637_1632316597.19842.json.gpg", "rb") as f:
            file_contents = f.read()

        with ssm_shared_gpg_setup:
            result = test_obj.decode_file(file_blob=file_contents)

        assert type(result) == bytes
