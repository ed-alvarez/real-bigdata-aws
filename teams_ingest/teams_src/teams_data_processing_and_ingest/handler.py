import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import aws_lambda_logging
from aws_lambda_context import LambdaContext

tenant_directory = Path(__file__).resolve().parent.parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))

from teams_settings import BOTO_LOG_LEVEL, LOG_FORMAT, LOG_LEVEL
from teams_src.teams_data_processing_and_ingest.teams_upload import TeamsUpload

log = logging.getLogger()


def setup_logging(aws_request_id: str):
    aws_lambda_logging.setup(
        level=LOG_LEVEL,
        boto_level=BOTO_LOG_LEVEL,
        aws_request_id=aws_request_id,
        module="%(module)s",
    )


def lambda_handler(event: Dict, context: LambdaContext) -> Dict:
    teams_upload_obj = TeamsUpload(aws_event=event, aws_context=context)
    return teams_upload_obj.teams_ingest_workflow()


if __name__ == "__main__":

    class LambdaContext:
        def __init__(self, time_limit_in_seconds=120):
            self.log_group_name = "local_test_log_group_name"
            self.log_stream_name = "local_test_log_stream_name"
            self.aws_request_id = "local_test_aws_request_id"

            self.start_time = datetime.now()
            self.time_limit_in_seconds = time_limit_in_seconds
            self.end_time = self.start_time + timedelta(seconds=self.time_limit_in_seconds)

        def get_remaining_time_in_millis(self):
            time_now = datetime.now()
            if time_now <= self.end_time:
                time_left = self.end_time - time_now
                time_left_milli = (time_left.seconds * 1000) + (time_left.microseconds / 1000)
            else:
                time_left_milli = 0
            return int(time_left_milli)

    items = [
        'dev-todo.teams/2023-03-28/user_7176ad28-5380-4962-a200-fd862534b526_20230328_1680099912400.json',
        'dev-todo.teams/2023-03-28/user_4867eb39-23f4-4843-a7f6-70f9c9c2f9e9_20230328_1680099926772.json',
    ]

    for item in items:
        print(
            lambda_handler(
                event={
                    "firm": "dev-oakley",
                    "period": "daily",
                    "tenant_name": "dev-oakley",
                    "tenant_id": "cab90704-9f9a-464f-9a7d-08116dc47cc3",
                    "user_ids": [],
                    "files_to_process": True,
                    "workflow_done": False,
                    "list_of_files_to_process": [item],
                    "list_of_files_processed": [],
                },
                context=LambdaContext(),
            )
        )
