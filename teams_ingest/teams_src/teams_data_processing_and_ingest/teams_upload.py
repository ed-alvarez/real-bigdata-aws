import logging
import sys
from pathlib import Path
from typing import Any, Dict

from aws_lambda_context import LambdaContext

tenant_directory = Path(__file__).resolve().parent.parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_settings import INGEST_SOURCE, STAGE, processingStage
from teams_src.teams_data_processing_and_ingest.user_chat_to_conversation import (
    ChatToConversation,
)
from teams_src.teams_shared_modules.step_funtion_data_classes import TeamsDecode
from teams_src.teams_shared_modules.teams_data_classes import ClientCreds

from shared.shared_src.s3.s3_helper import S3Helper

log = logging.getLogger()


class TeamsUpload:
    def __init__(self, aws_event: Dict[str, Any], aws_context: Dict):
        self._aws_event: TeamsDecode = TeamsDecode(**aws_event)
        self._aws_context: LambdaContext = aws_context
        self._s3_client = S3Helper(client_name=self._aws_event.firm, ingest_type=INGEST_SOURCE)

    def teams_ingest_workflow(self) -> Dict:
        log.info(f"Entry event {self._aws_event}")

        if self._aws_event.list_of_files_to_process:
            self._aws_event.workflow_done = False
            client_creds: ClientCreds = ClientCreds(firm=self._aws_event.firm, tenant_id=self._aws_event.tenant_id)

            s3_uri_todo_user_conversations: str = self._aws_event.list_of_files_to_process[0]
            log.debug(f"Processing TODO URI {s3_uri_todo_user_conversations}")

            user_cdr_conversation_list = self._s3_client.get_file_content(s3_uri_todo_user_conversations, as_dict=True)

            user_id = s3_uri_todo_user_conversations.split("_")[0].split("/")[-1]

            conversations_obj: ChatToConversation = ChatToConversation(
                list_of_messages=user_cdr_conversation_list,
                user_id=user_id,
                s3_client=self._s3_client,
                client_creds=client_creds,
                aws_event=self._aws_event,
                aws_context=self._aws_context,
            )
            try:
                conversations_obj.convert_user_chat_to_conversation()
            except Exception as ex:
                log.exception(f"Error processing JSON File {ex}")
                raise ex

            if conversations_obj.conversation_processed:
                self._mark_processed_check_if_finished(self._s3_client)
        return self._aws_event.to_json()

    def _mark_processed_check_if_finished(self, s3_client):
        todo_message_processed = self._aws_event.list_of_files_to_process.pop(0)
        new_processed_uri = todo_message_processed.replace(processingStage.todo.value, processingStage.processed.value).replace(
            self._aws_event.firm, ""
        )

        if copied := s3_client.copy_file_between_folders(src_key=todo_message_processed, dst_key=new_processed_uri):
            if "prod" in STAGE:
                s3_client.delete_file(file_key=todo_message_processed)
            s3_client.copy_file_between_folders(
                src_key=new_processed_uri,
                dst_key=new_processed_uri.replace(processingStage.processed.value, processingStage.archived.value).replace(
                    self._aws_event.firm, ""
                ),
            )
            self._aws_event.list_of_files_processed.append(new_processed_uri)

        if len(self._aws_event.list_of_files_to_process) == 0:
            self._aws_event.files_to_process = False
            self._aws_event.workflow_done = True
