import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

tenant_directory = Path(__file__).resolve().parent.parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from aws_lambda_context import LambdaContext
from elasticsearch import exceptions
from iteration_utilities import unique_everseen
from teams_settings import INGEST_SOURCE, UPLOAD_TO_ES
from teams_src.teams_data_processing_and_ingest.elastic_search.es_bulk import (
    TEAMS_esBulk,
)
from teams_src.teams_data_processing_and_ingest.message_es_bulk_object import (
    TeamsBulkMessages,
)
from teams_src.teams_data_processing_and_ingest.teams_conversation.conversation_to_es import (
    ConvertConversation,
)
from teams_src.teams_shared_modules.step_funtion_data_classes import TeamsDecode
from teams_src.teams_shared_modules.teams_data_classes import ClientCreds

from shared.shared_src.s3.s3_helper import S3Helper

log = logging.getLogger()


class ChatToConversation:
    """
    convert list of all messages by user into messages by conversations
    get unique chat ID's
    for each chatID
        get list of messages
        de dupe list
        sort list by date order
        process each chat list
            process message for Address to from
            process message for attachment decode
            add processed message to ES message class
        save conversations to file - by day
        Bulk upload conversation to Elasticsearch
    """

    def __init__(
        self,
        list_of_messages: List[Dict],
        user_id: str,
        s3_client: S3Helper,
        aws_event: TeamsDecode,
        aws_context: LambdaContext,
        client_creds: ClientCreds = None,
    ) -> None:
        self._list_of_messages: List[Dict] = list_of_messages
        self._aws_event: TeamsDecode = aws_event
        self._user_id = user_id
        self._aws_context: LambdaContext = aws_context
        self._s3_client: S3Helper = s3_client or S3Helper(client_name=self.aws_event.firm, ingest_type=INGEST_SOURCE)
        self._all_messages_parse_complete = False
        self._client_creds: ClientCreds = client_creds or ClientCreds(client=self._aws_event.firm, tenant_id=self._aws_event.tenant_id)
        self.conversation_processed = False

        if UPLOAD_TO_ES:
            self._es_bulk: TEAMS_esBulk = TEAMS_esBulk()

    @property
    def allMessageParseComplete(self) -> bool:
        return self._all_messages_parse_complete

    @property
    def conversationItemNextStart(self) -> int:
        return self._conversation_next_item

    @property
    def messageNextItemStart(self) -> int:
        return self._message_start_item

    def _generate_chat_ids_to_process(self, conversations: List[Dict]) -> set:
        chat_ids: set = {conversation["chatId"] for conversation in conversations}
        return chat_ids

    def _order_messages(self, conversations: List[Dict]) -> List[Dict]:
        unique_items: List[Dict] = list(unique_everseen(conversations))

        unique_items.sort(key=lambda item: item["createdDateTime"], reverse=False)
        return unique_items

    def _group_by_chatid(self, conversations: List[Dict]) -> Dict[str, List[Dict]]:
        groups = defaultdict(list)
        for message in conversations:
            chatid = message["chatId"]
            groups[chatid].append(message)
        return dict(groups)

    def convert_user_chat_to_conversation(self) -> None:
        try:
            chat_ids: set = self._generate_chat_ids_to_process(conversations=self._list_of_messages)
            log.info(f"Processing the following Chat IDS {chat_ids}")
            ordered_conversations: list = self._order_messages(conversations=self._list_of_messages)
            conversations_grouped: list = list(self._group_by_chatid(ordered_conversations).values())
        except KeyError as error:
            log.error(f"Wrong chat parsing {error}")

        for conversation in conversations_grouped:
            converted_chat_obj: ConvertConversation = ConvertConversation(
                conversation=conversation,
                aws_event=self._aws_event,
                aws_context=self._aws_context,
            )

            try:
                conversation: TeamsBulkMessages = converted_chat_obj.enumerate_conversation()

            except Exception as ex:
                log.exception(f"Error processing single conversation {conversation}")
                raise ex

            # Upload all parts of a teams conversation to ES
            if UPLOAD_TO_ES:
                log.info("Upload Teams_conversation to ElasticSearch")
                try:
                    self._es_bulk.upload_data(es_bulk_data=conversation)
                    log.info("Conversation sucessfully Uploaded to ElasticSearch")
                    self.conversation_processed = True
                except exceptions.ElasticsearchException as ex:
                    log.exception(ex)
                    log.error("Error Uploading Conversation to ElasticSearch")
                    raise ex
            return
