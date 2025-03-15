import logging
import re
from datetime import datetime
from email.utils import formataddr
from typing import Dict, List, Optional, Tuple

from aws_lambda_context import LambdaContext
from datefinder import find_dates
from teams_settings import (
    AWS_TIMEOUT_MILLISECONDS,
    FINGERPRINT_TYPE,
    MESSAGE_BATCH_SIZE,
    MESSAGE_LIST_SIZE,
    processingStage,
)
from teams_src.teams_data_processing_and_ingest.attachment_parser.route_attachment import (
    TeamsAttachmentDecode,
)
from teams_src.teams_data_processing_and_ingest.elastic_search.es_teams_index import (
    TEAMS,
    BodyDetail,
    Schema,
)
from teams_src.teams_data_processing_and_ingest.elastic_search.es_teams_index import (
    attachment as ES_ATTACHMENT,
)
from teams_src.teams_data_processing_and_ingest.elastic_search.es_teams_index import (
    fingerprint_meta,
    teams_id,
)
from teams_src.teams_data_processing_and_ingest.message_es_bulk_object import (
    ConversationAudience,
    TeamsBulkMessages,
)
from teams_src.teams_data_processing_and_ingest.teams_conversation import (
    attachment_helper_functions,
    image_helper_functions,
)
from teams_src.teams_shared_modules.step_funtion_data_classes import TeamsDecode
from teams_src.teams_shared_modules.teams_data_classes import (
    ClientCreds,
    DynamoClientRecord,
    DynamoTeamsUser,
    imageURL,
)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

log = logging.getLogger()


class ConvertConversation:
    def __init__(
        self,
        conversation: List[Dict],
        aws_event: TeamsDecode,
        aws_context: LambdaContext,
        client_creds: ClientCreds = None,
    ) -> None:
        self._input_conversation: List[Dict] = conversation
        self._aws_event: TeamsDecode = aws_event
        self._client_creds: ClientCreds = client_creds or ClientCreds(firm=self._aws_event.firm, tenant_id=self._aws_event.tenant_id)
        self._aws_context: LambdaContext = aws_context
        self._customer = aws_event.firm
        # Dealing with batches loops & timeouts
        self._conversation_processing_completed: bool = False

    @property
    def conversationItemNextStart(self):
        return self._next_item

    @property
    def conversationProccessingComplete(self):
        return self._conversation_processing_completed

    def _generate_zip_file_name(self, file: str) -> str:
        clean_str: str = f"{self._aws_event.tenant_name}-{file}"
        return clean_str

    def _search_for_email(self, uuid: str) -> str:
        list_of_users = DynamoClientRecord(client=self._aws_event.firm).get_dynamo_client().users
        if dynamo_user := next((element for element in list_of_users if element['iD'] == uuid), None):
            return dynamo_user['uPN']
        address: str = ''
        return address

    def _extract_user_from_message(self, user: Optional[Dict]) -> teams_id:
        """
            User format
            "id": "0343ab0a-2dee-4672-bc86-20af382ea5d8",
            "displayName": "Denny Biasiolli",
            "userIdentityType": "aadUser"
        :param user: Dict from the message of user information
        :return: teams_id and ES object for the user

        """
        if user is None:
            log.debug("Probably a Bot App converastion, User: None!")
            user = {}

        teams_user: teams_id = teams_id()
        try:
            teams_user.uuid = user.get("id", "0000000000-0000-0000-0000000000000")
            teams_user.fullname = user.get("displayName", "No Name")
            teams_user.emailaddress = self._search_for_email(uuid=user.get("id", teams_user.uuid))
            if teams_user.emailaddress:
                teams_user.domain = teams_user.emailaddress.split("@")[-1]
            else:
                log.debug(f"User {teams_user.fullname} is not in lookup list")
                teams_user.domain = ""
        except Exception as error:
            log.info(f"user is not present, may be a bot conversation! {error}")
        return teams_user

    def _remove_html_tags(self, text: str) -> str:
        """Remove html tags from a string"""
        clean: re = re.compile("<.*?>")
        return re.sub(clean, "", text)

    def _convert_body(self, body: Dict, date_time: datetime) -> Tuple[str, List[str]]:
        image_archive_file_names = []
        body_content: str = ""
        if body["contentType"] == "text":
            body_content = body["content"]
        elif body["contentType"] == "html":
            body_content = self._remove_html_tags(text=body["content"])
            images: List[imageURL] = image_helper_functions.get_images(content=body["content"], client_creds=self._client_creds)
            for image in images:
                zip_file_name: str = self._generate_zip_file_name(file=image.message_id)
                file_name: str = image_helper_functions.add_images_to_zip_file(
                    client=self._customer,
                    zip_file_name=zip_file_name,
                    file_name=image.hosted_contents_id,
                    content=image.content,
                    date_time=date_time,
                )
                image_archive_file_names.append(file_name)

        return body_content, image_archive_file_names

    def _generate_summary_user_info(self, user: teams_id) -> str:
        user = formataddr((user.fullname, user.emailaddress))
        return user

    def _generate_to_field(self, to_detail: List[teams_id]) -> List[str]:
        to_detail_list: List[str] = [self._generate_summary_user_info(user=item) for item in to_detail]
        return to_detail_list

    def _generate_body_detail(self, body: str, image_file_archive: List) -> BodyDetail:
        body_detail = BodyDetail()
        body_detail.has_body = False
        if body:
            sid = SentimentIntensityAnalyzer()
            body_detail.has_body = True
            body_detail.body_sentiment = sid.polarity_scores(body)
            body_detail.body_size = len(body)
            body_detail.image_file_archive = image_file_archive
        return body_detail

    def _parse_attachments(
        self,
        attachments: List[Dict],
        date_time: datetime,
        client_creds: ClientCreds = None,
    ) -> List[ES_ATTACHMENT]:
        client_creds = client_creds or self._client_creds
        es_attachments: List = []
        for attachment in attachments:
            if attachment_helper_functions.is_attachment_a_url_link(attachment=attachment):
                attachment_decode_obj: TeamsAttachmentDecode = TeamsAttachmentDecode(
                    teams_attachment=attachment, client_creds=client_creds
                )
                es_attachment: ES_ATTACHMENT = attachment_decode_obj.route_attachment()
                zip_file_name: str = self._generate_zip_file_name(file=attachment["id"])
                es_attachment.tar_file_location = attachment_helper_functions.add_attachment_to_zip_file(
                    client=self._customer,
                    zip_file_name=zip_file_name,
                    file_name=attachment["name"],
                    content=attachment_decode_obj.attachmentBytes,
                    date_time=date_time,
                )
                es_attachments.append(es_attachment)
        return es_attachments

    def _populate_fingerprint_meta(self, key: str, message_time: datetime, lambda_id: str) -> fingerprint_meta:
        fingerprint_meta_data: fingerprint_meta = fingerprint_meta()
        fingerprint_meta_data.client = self._customer
        fingerprint_meta_data.bucket = f"{self._customer}.ips"
        fingerprint_meta_data.key = key.replace(processingStage.todo.value, processingStage.processed.value)
        fingerprint_meta_data.processed_time = datetime.now()
        fingerprint_meta_data.time = message_time
        fingerprint_meta_data.type = FINGERPRINT_TYPE
        fingerprint_meta_data.aws_lambda_id = lambda_id
        fingerprint_meta_data.schema = Schema.version

        return fingerprint_meta_data

    def _format_message_time_to_datetime(self, message_date: str) -> datetime:
        """
        "createdDateTime": "2021-01-27T14:39:59.793Z"
        """
        if matches := list(find_dates(message_date)):
            return matches[0]
        else:
            return datetime.now()

    def enumerate_conversation(self) -> TeamsBulkMessages:
        users_in_conversation: ConversationAudience = ConversationAudience()
        conversation_es_bulk: TeamsBulkMessages = TeamsBulkMessages()

        for message in self._input_conversation:
            if message.get("from", {}) is None:
                message['from'] = {}
            message_es: TEAMS = TEAMS()
            message_es.conversationid = message["chatId"]
            message_es.messageid = message["id"]
            message_es.datetime = self._format_message_time_to_datetime(message_date=message["createdDateTime"])
            message_es.from_detail = self._extract_user_from_message(user=message.get("from", {}).get("user", {}))
            users_in_conversation.add_user(message_es.from_detail)
            message_es.from_ = self._generate_summary_user_info(user=message_es.from_detail)

            message_es.to_detail = users_in_conversation.get_to_list(messageFrom=message_es.from_detail)
            message_es.to = self._generate_to_field(to_detail=message_es.to_detail)
            body, file_names = self._convert_body(
                body=message["body"],
                date_time=message_es.datetime,
            )
            message_es.body = body
            message_es.body_detail = self._generate_body_detail(body=message_es.body, image_file_archive=file_names)
            message_es.attachments = self._parse_attachments(
                attachments=message["attachments"],
                date_time=message_es.datetime,
            )
            message_es.fingerprint = self._populate_fingerprint_meta(
                key=self._aws_event.list_of_files_to_process[0],
                message_time=message_es.datetime,
                lambda_id=self._aws_context.aws_request_id,
            )

            conversation_es_bulk.add_teams_message(message_es)

        return conversation_es_bulk
