"""
Test for teams_data_download lambda function
"""

import sys
from pathlib import Path

from mock import patch

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_src.teams_data_download.handler import lambda_handler
from teams_tests.data.test_input_resources.input_teams_data_downloader import (
    expected_output_teams_data_downloader,
    input_teams_data_downloader,
)


class TestTeamsDataDownloadHandler:
    def test_lambda_handler(self, teams_s3_client, test_lambda_context, dynamo_db_teams_setup, ssm_teams_setup):
        with ssm_teams_setup:
            with patch("teams_settings.UPLOAD_TO_ES", False):
                result = lambda_handler(event=input_teams_data_downloader, context=test_lambda_context)
                assert result
                assert expected_output_teams_data_downloader.keys() == result.keys()
