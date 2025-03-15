"""This module downloads the conversations from the Teams REST API and saves them to S3"""
import logging
import sys
from pathlib import Path
from typing import Any, Dict

import aws_lambda_logging

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_settings import BOTO_LOG_LEVEL, LOG_LEVEL
from teams_src.teams_data_fetch_conversation.conversation_fetcher import (
    ConversationFetcher,
)
from teams_src.teams_shared_modules.step_funtion_data_classes import TeamsDecode

log = logging.getLogger()


def lambda_handler(event: Dict[str, Any], context: Dict):
    aws_lambda_logging.setup(
        level=LOG_LEVEL,
        boto_level=BOTO_LOG_LEVEL,
        aws_request_id=context.aws_request_id,
        module="%(module)s",
    )

    response: TeamsDecode = fetch_one_to_one_chat(event=event)
    return response.to_json()


def fetch_one_to_one_chat(event: Dict[str, Any]) -> TeamsDecode:
    teams_event: TeamsDecode = TeamsDecode(**event)

    log.info(event)
    conversation_fetcher = ConversationFetcher(event=teams_event)

    if s3_uri_to_process := conversation_fetcher.one_to_one_chats():
        teams_event.list_of_files_to_process.extend(s3_uri_to_process)
        teams_event.files_to_process = True
    if len(teams_event.user_ids) == 0 and teams_event.files_to_process:
        teams_event.workflow_done = True
    return teams_event


if __name__ == "__main__":

    files_to_process = []

    class context:
        def __init__(self):
            self.aws_request_id = "no_id"

    users = [
        "541e7d82-ea07-43e4-8168-115c609569ae",
        "7176ad28-5380-4962-a200-fd862534b526",
        "d20d016a-9a4c-490e-876d-b7fe1fb4b435",
        "9de3ac6c-74f2-4303-b177-b74346f115e2",
        "513e4a6f-c590-4452-adbd-01ca4110c2d5",
        "e5fd76e2-9381-48a6-8815-84c2f738b611",
        "5625e4d8-2974-44db-a31b-a6819dc4011a",
        "a869f1b3-fe49-443d-b3ed-3119d58987fc",
        "4d4e8078-1836-4d2d-a731-6f3f248de2c5",
        "9db92424-c67e-48f1-be2e-88500d746882",
        "9d504ea1-7515-422b-a013-d1def5a003f6",
        "e625abcc-98c6-497f-9331-79dc688bc7af",
        "4867eb39-23f4-4843-a7f6-70f9c9c2f9e9",
    ]
    for user in users:
        daily_event = {
            "firm": "dev-oakley",
            "period": "daily",
            "tenant_name": "dev-oakley",
            "tenant_id": "cab90704-9f9a-464f-9a7d-08116dc47cc3",
            "start_date": "2023-03-28",
            "end_date": "2023-03-29",
            "user_ids": [user],
        }
        response = lambda_handler(daily_event, context=context())
        print(response)
        if response.get('list_of_files_to_process'):
            todo_file = response.get('list_of_files_to_process').pop()
            files_to_process.append(todo_file)
    print(files_to_process)
