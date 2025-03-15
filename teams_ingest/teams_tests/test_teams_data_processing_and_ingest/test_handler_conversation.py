"""
Test for teams_data_download lambda function
"""
import sys
from pathlib import Path
from unittest import mock
from unittest.mock import patch

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))

from teams_tests.data.test_input_resources.input_teams_data_processing_and_ingest import (
    input_teams_processing_and_ingest,
)

from shared.shared_src.es.es_client import ElasticSearchClient
from shared.shared_src.s3.s3_helper import S3Helper


class TestTeamsDataProcessingAndIngest:
    @patch.object(S3Helper, "get_file_content", return_value=[])
    @patch.object(ElasticSearchClient, "get_client")
    def test_lambda_handler(
        self,
        mocked_get_client,
        mocked_get_file_content,
        teams_s3_client,
        test_lambda_context,
        dynamo_db_teams_setup,
        ssm_teams_setup,
        teams_ddb_client,
    ):
        with mock.patch(
            "teams_src.teams_shared_modules.teams_data_classes.DynamoClientRecord.ddb_client",
            teams_ddb_client,
        ):
            with ssm_teams_setup:
                with patch("teams_settings.UPLOAD_TO_ES", False):
                    from teams_src.teams_data_processing_and_ingest.handler import (
                        lambda_handler,
                    )

                    result = lambda_handler(event=input_teams_processing_and_ingest, context=test_lambda_context)
                    assert result

    def test_empty_files_to_process(self):
        """
        Check output when there is no file to be processed
        """
        # TODO
        pass

    def test_s3_uri_from_file_to_process_does_not_exist(self):
        """
        Test when s3 uri from file to be processed is not available/does not exist in S3
        """
        # TODO
        pass

    def test_get_user_id_from_string_fail(self):
        """
        Test that string operation to get user id failed
        """
        # TODO
        pass

    def test_convert_user_chat_to_conversation_raise_exception(self):
        """
        Test convert_user_chat_to_conversation raise an exception
        """
        # TODO
        pass
