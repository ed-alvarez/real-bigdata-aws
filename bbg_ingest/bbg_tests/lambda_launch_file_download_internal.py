import os

import boto3
from moto import mock_s3, mock_ssm

from bbg_ingest.bbg_tests import MockSFTP
from bbg_ingest.lambdas import handler


class LambdaContext:
    def __init__(self):
        self.log_group_name = "local_test_log_stream_name"
        self.log_stream_name = "local_test_log_stream_name"
        self.aws_request_id = "local_test_aws_request_id"


# run in stage mode with: DEV_MODE=0 pytest bbg_tests
if os.environ.get("DEV_MODE", "1") == "1":
    TODO_FOLDER = "dev.todo.bbg"
else:
    TODO_FOLDER = "todo.bbg"
    os.environ["STAGE"] = "stage"
    os.environ["AWS_EXECUTION_ENV"] = "1"

CLIENT_NAME = "testing"
# FIXTURES_DIR = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir)) + '/fixtures'
FIXTURES_DIR = "/bbg_tests/fixtures"
os.environ["SSH_HOST"] = "localhost"
os.environ["SSH_PORT"] = "3375"
SFTP_PARAMS = {
    "host": os.environ["SSH_HOST"],
    "port": int(os.environ["SSH_PORT"]),
    "keyfile": FIXTURES_DIR + "/sftpkey",
    "level": "DEBUG",
}
INPUT = {"bbg_client_id": "mc1234", "client_name": CLIENT_NAME, "bbg_manifest": "DAILY"}
OUTPUT = {
    "client_name": CLIENT_NAME,
    "files_downloaded": [
        f"{TODO_FOLDER}/2019-03-29/downloaded/f848135.msg.190329.xml.gpg",
        f"{TODO_FOLDER}/2019-03-29/downloaded/f848135.msg.190329.xml.sig",
    ],
    "files_decoded": "",
    "has_files": True,
}
BUCKET_NAME = f"{CLIENT_NAME}.ips"


@mock_s3
@mock_ssm
def test_populated_manifest():
    # create dummy parameter store
    ssm = boto3.client("ssm")
    with open("/bbg_tests/fixtures/sftp/sftpkey", "r") as myfile:
        ssh_key = myfile.read()
    ssm.put_parameter(
        Name="/testing/bbgsshkey.pem",
        Description="BBG SSH Key",
        Value=ssh_key,
        Type="SecureString",
    )

    ssm.put_parameter(
        Name="/testing/bbgsshkeypass",
        Description="BBG SSH passphrase",
        Value="Fingerprint1",
        Type="SecureString",
    )

    # create mock s3 bucket
    conn = boto3.resource("s3", region_name="eu-west-1")
    bucket = conn.create_bucket(Bucket=BUCKET_NAME)

    # download files from virtual sftp server and check output event matches
    with MockSFTP(**SFTP_PARAMS, path=FIXTURES_DIR + "/sftp/msg_only"):
        result = handler.lambda_handler(INPUT, LambdaContext())
        print(result, OUTPUT)

    # check original files are now present in the s3 bucket
    bucket_keys = [file.key for file in bucket.objects.all()]
    # print('bucket_keys', bucket_keys)
    for f in OUTPUT["files_downloaded"] + [f"{TODO_FOLDER}/2019-03-29/downloaded/daily_manifest_current.txt"]:
        print(f, bucket_keys)


if __name__ == "__main__":
    test_populated_manifest()
