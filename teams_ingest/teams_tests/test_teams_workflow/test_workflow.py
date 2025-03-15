import sys
from pathlib import Path

import pytest

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))

from teams_src.teams_data_download.handler import lambda_handler as lambda_ids
from teams_src.teams_data_fetch_conversation.handler import (
    lambda_handler as lambda_download,
)
from teams_src.teams_data_processing_and_ingest.handler import (
    lambda_handler as lambda_process,
)


@pytest.mark.skip(reason="WIP")
@pytest.mark.usefixtures("launch_event_daily", "aws_credentials", "s3_client", "ssm_client", "ddb_client")
class TestIntegration:
    def test_lambda_ids(self, launch_event_daily, context_param):
        pytest.first_event = lambda_ids(launch_event_daily, context_param)

    def test_lambda_download(self, context_param):
        pytest.second_event = lambda_download(pytest.first_event, context_param)

    def test_lambda_process(self, context_param):
        pytest.third_event = lambda_process(pytest.second_event, context_param)
