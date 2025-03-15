import os

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

CLIENT_NAME = "test"

INPUT_1 = {"bbg_client_id": "mc913915589", "client_name": CLIENT_NAME, "bbg_manifest": "DAILY"}

INPUT_2 = {
    "bbg_client_id": "mc913915589",
    "client_name": CLIENT_NAME,
    "bbg_manifest": "ARCHIVE",
    "manifest_date": "200818",
}


def test_populated_manifest():
    result = handler.lambda_handler(INPUT_1, LambdaContext())
    print(result)


if __name__ == "__main__":
    test_populated_manifest()
