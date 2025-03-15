"""This module downloads the conversations from the Teams REST API and saves them to S3"""
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

import aws_lambda_logging

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))

from teams_settings import BOTO_LOG_LEVEL, INGEST_SOURCE, LOG_LEVEL
from teams_src.teams_data_download.download_user_list import GrabUserTeamIDs
from teams_src.teams_shared_modules.step_funtion_data_classes import (
    TeamsDecode,
    TeamsEvent,
)
from teams_src.teams_shared_modules.teams_data_classes import DynamoClientRecord

from shared.shared_src.s3.s3_helper import S3Helper

log = logging.getLogger()


def lambda_handler(event: Dict[str, Any], context: Dict):
    aws_lambda_logging.setup(level=LOG_LEVEL, boto_level=BOTO_LOG_LEVEL, aws_request_id=context.aws_request_id, module="%(module)s")
    response: TeamsDecode = teams_ingest_workflow(event=event)
    return response.to_json()


def teams_ingest_workflow(event: Dict[str, Any]) -> TeamsEvent:
    teams_event: TeamsEvent = TeamsEvent(**event)
    log.info(event)
    s3_client: S3Helper = S3Helper(client_name=teams_event.firm, ingest_type=INGEST_SOURCE)

    try:
        user_ids = users_at_account(event=teams_event, s3_client=s3_client)
        log.info(f"User IDs = {user_ids}")
        teams_event.user_ids = user_ids
    except Exception as ex:
        log.exception(f"ERROR in processing workflow {ex}")
    return teams_event


def users_at_account(event: TeamsEvent, s3_client: S3Helper) -> List:
    dynamo_client_record: DynamoClientRecord = DynamoClientRecord(client=event.tenant_name).get_dynamo_client()
    response: List = []
    log.debug("Setup 1 2 1 chats object")
    obj_one_to_one_chats: GrabUserTeamIDs = GrabUserTeamIDs(event=event, dynamo_client_record=dynamo_client_record)

    try:
        response = obj_one_to_one_chats.get_users_ids(s3_client)
    except Exception as ex:
        log.exception("ERROR in processing one to one chat")
        raise ex

    return response
