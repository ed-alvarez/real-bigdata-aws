import sys
from pathlib import Path

from mock import patch

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))

from teams_src.teams_shared_modules.teams_data_classes import ClientCreds
from teams_tests.data.list_of_all_messages import all_messages
from teams_tests.data.stepfunction_data import teams_history_decode, teams_history_event

from shared.shared_src.es.es_client import ElasticSearchClient


class TestFunction:
    @patch.object(ElasticSearchClient, "get_client")
    def test_generate_chat_ids_to_process(self, mocked_get_client, ssm_teams_setup, test_lambda_context, s3_client):
        with patch("teams_settings.UPLOAD_TO_ES", False):
            with ssm_teams_setup:
                from teams_src.teams_data_processing_and_ingest.user_chat_to_conversation import (
                    ChatToConversation,
                )

                client_creds: ClientCreds = ClientCreds(firm="test-ips", tenant_id="a38e65be-fb2c-4ab0-9084-199607af9f21")
                chat_to_conversation_obj: ChatToConversation = ChatToConversation(
                    list_of_messages=all_messages,
                    user_id="",
                    s3_client=s3_client,
                    client_creds=client_creds,
                    aws_event=teams_history_decode,
                    aws_context=test_lambda_context,
                )
                result = chat_to_conversation_obj._generate_chat_ids_to_process(all_messages)
                print(f"SHOW MY RESULTS {result}")
                assert result == {
                    "19:28ad04f7-55d2-4fe8-b917-52f3c24ab13d_9a618be6-2988-4202-84cf-634ecc976bf2@unq.gbl.spaces",
                    "19:28ad04f7-55d2-4fe8-b917-52f3c24ab13d_9d3a6f3c-0945-4a0f-a34a-035d33eff064@unq.gbl.spaces",
                    "19:0343ab0a-2dee-4672-bc86-20af382ea5d8_9d3a6f3c-0945-4a0f-a34a-035d33eff064@unq.gbl.spaces",
                    "19:0f97ac84-386f-41fe-9902-77beded8033a_9a618be6-2988-4202-84cf-634ecc976bf2@unq.gbl.spaces",
                }
