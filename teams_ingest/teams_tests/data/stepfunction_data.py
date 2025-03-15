from typing import Dict

from teams_src.teams_shared_modules.step_funtion_data_classes import (
    TeamsDecode,
    TeamsEvent,
)

history_event: Dict = {
    "firm": "test-ips",
    "period": "historical",
    "tenant_name": "test-ips",
    "tenant_id": "00000-00000-000000-000000",
    "start_date": "2021-01-18",
    "end_date": "2021-01-19",
}

teams_history_event: TeamsEvent = TeamsEvent(**history_event)

teams_history_decode: TeamsDecode = TeamsDecode(**history_event)
teams_history_decode.list_of_files_to_process = ["dev.todo.teams/2021-01-18/all_one_to_one_chats.json"]

decode_event: Dict = {
    "firm": "test-ips",
    "period": "historical",
    "tenant_name": "test-ips",
    "tenant_id": "00000-00000-000000-000000",
    "start_date": "2021-01-18",
    "end_date": "2021-01-19",
    "files_to_process": True,
    "list_of_files_to_process": ["dev.todo.teams/2021-01-18/all_one_to_one_chats.json"],
    "list_of_files_processed": [],
    "conversation_number": 0,
    "message_number": 0,
}
