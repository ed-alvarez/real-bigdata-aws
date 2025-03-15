import pytest
from bbg_src.files_to_decode_lambda.gpg_file_decode import BBGGPGHelper


class TestEndToEnd:
    def test_gpg_file_decode(self, ssm_bbg_gpg_harness, s3_bbg_gpg_harness, s3_client):
        file_to_decode = "Architecture High Level.docx.gpg"
        file_after_decode = "Architecture High Level.docx"
        with ssm_bbg_gpg_harness:
            with s3_bbg_gpg_harness:
                decode_file = BBGGPGHelper(client_name="testing")
                decode_file.decode_file(decode_file_name=file_to_decode, decoded_file_name=file_after_decode)
                object = s3_client.get_object(Bucket="testing.ips", Key=file_after_decode)
                assert object["ContentLength"] == pytest.approx(2251597)
