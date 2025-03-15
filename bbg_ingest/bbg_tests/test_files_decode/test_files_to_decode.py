from contextlib import contextmanager
from pathlib import Path

from bbg_src.files_to_decode_lambda.files_to_decode import BBGFileDecode

BASE_DIR = Path(__file__).resolve().parent.parent
CLIENT_NAME = "testing"
FIXTURES_DIR = f"{BASE_DIR}/fixtures"
BUCKET_NAME = f"{CLIENT_NAME}.ips"


class TestStepFunctionMessages:
    @contextmanager
    def s3_setup(self, s3_client):
        bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": "eu-west-1"})

        s3_mock_upload_list = []
        for type in ["ib", "msg", "dscl"]:
            bbg_file = (
                f"todo.bbg/2021-02-16/downloaded/f947949.{type}.210216.xml.gpg",
                f"{FIXTURES_DIR}/Decode/all/f848135.{type}.190329.xml.gpg",
            )
            s3_mock_upload_list.append(bbg_file)

            bbg_file_sig = (
                f"todo.bbg/2021-02-16/downloaded/f947949.{type}.210216.xml.sig",
                f"{FIXTURES_DIR}/Decode/all/f848135.{type}.190329.xml.sig",
            )
            s3_mock_upload_list.append(bbg_file_sig)

        att_file = (
            f"todo.bbg/2021-02-16/downloaded/f947949.att.210216.tar.gz.gpg",
            f"{FIXTURES_DIR}/Decode/all/f848135.att.190329.tar.gz.gpg",
        )
        s3_mock_upload_list.append(att_file)

        att_file_sig = (
            f"todo.bbg/2021-02-16/downloaded/f947949.att.210216.tar.gz.sig",
            f"{FIXTURES_DIR}/Decode/all/f848135.att.190329.tar.gz.sig",
        )
        s3_mock_upload_list.append(att_file_sig)

        for file_pair in s3_mock_upload_list:
            self.mock_s3_upload(local_filename=file_pair[1], s3_key=file_pair[0], s3_client=s3_client)

        yield

    def mock_s3_upload(self, local_filename, s3_key, s3_client):
        with open(local_filename, "rb") as f:
            s3_client.upload_fileobj(f, BUCKET_NAME, s3_key)

    @contextmanager
    def ssm_setup(self, ssm_client):
        with open(f"{BASE_DIR}/fixtures/Decode/bbgprivkey.pem", "r") as myfile:
            ssh_key = myfile.read()
        ssm_client.put_parameter(
            Name="/testing/bbgprivkey.pem",
            Description="BBG Decode Key",
            Value=ssh_key,
            Type="String",
        )

        ssm_client.put_parameter(
            Name="/testing/bbgprivkeypass",
            Description="BBG Decode passphrase",
            Value="drugs.declaim.calendar",
            Type="String",
        )
        yield

    def test_initial_condition(self, s3_client, ssm_client):
        input_message = {
            "client_name": CLIENT_NAME,
            "files_downloaded": [
                "todo.bbg/2021-02-16/downloaded/f947949.ib.210216.xml.gpg",
                "todo.bbg/2021-02-16/downloaded/f947949.ib.210216.xml.sig",
                "todo.bbg/2021-02-16/downloaded/f947949.att.210216.tar.gz.gpg",
                "todo.bbg/2021-02-16/downloaded/f947949.att.210216.tar.gz.sig",
                "todo.bbg/2021-02-16/downloaded/f947949.msg.210216.xml.gpg",
                "todo.bbg/2021-02-16/downloaded/f947949.msg.210216.xml.sig",
                "todo.bbg/2021-02-16/downloaded/f947949.dscl.210216.xml.gpg",
                "todo.bbg/2021-02-16/downloaded/f947949.dscl.210216.xml.sig",
            ],
            "files_decoded": [],
            "has_files": True,
            "error": False,
            "error_msg": "",
            "bbg_client_id": "mc1031925153",
            "bbg_manifest": "DAILY",
            "manifest_date": "210216",
            "wait_until": "",
        }

        output_message = {
            "client_name": CLIENT_NAME,
            "files_downloaded": [
                "todo.bbg/2021-02-16/downloaded/f947949.ib.210216.xml.sig",
                "todo.bbg/2021-02-16/downloaded/f947949.att.210216.tar.gz.gpg",
                "todo.bbg/2021-02-16/downloaded/f947949.att.210216.tar.gz.sig",
                "todo.bbg/2021-02-16/downloaded/f947949.msg.210216.xml.gpg",
                "todo.bbg/2021-02-16/downloaded/f947949.msg.210216.xml.sig",
                "todo.bbg/2021-02-16/downloaded/f947949.dscl.210216.xml.gpg",
                "todo.bbg/2021-02-16/downloaded/f947949.dscl.210216.xml.sig",
            ],
            "files_decoded": [
                "todo.bbg/2021-02-16/decoded/f947949.ib.210216.xml",
            ],
            "has_files": True,
            "error": False,
            "error_msg": "",
            "bbg_client_id": "mc1031925153",
            "bbg_manifest": "DAILY",
            "manifest_date": "210216",
            "wait_until": "",
            "bbg_files": {
                "MSG_XML_to_process": False,
                "MSG_file_name": "",
                "MSG_ATT_file_name": "",
                "MSG_XML_record_number": 0,
                "IB_XML_to_process": True,
                "IB_file_name": "todo.bbg/2021-02-16/decoded/f947949.ib.210216.xml",
                "IB_ATT_file_name": "",
                "IB_XML_record_number": 0,
            },
        }

        with self.ssm_setup(ssm_client):
            with self.s3_setup(s3_client):
                decode_msg = BBGFileDecode(event=input_message)
                result = decode_msg.files_to_decode()
                assert result == output_message
