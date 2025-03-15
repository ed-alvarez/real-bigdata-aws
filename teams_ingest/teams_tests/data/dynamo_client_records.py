from datetime import datetime

from teams_src.teams_shared_modules.teams_data_classes import (
    DynamoClientRecord,
    DynamoTeamsUser,
)

dynamo_teams_user_1: DynamoTeamsUser = DynamoTeamsUser(
    uPN="mike@ip-sentinel.com",
    iD="9d3a6f3c-0945-4a0f-a34a-035d33eff064",
    date_added=datetime(2021, 1, 27, 10, 12, 35, 26102),
)
dynamo_teams_user_2: DynamoTeamsUser = DynamoTeamsUser(
    uPN="sean@fingerprint-supervision.com",
    iD="9a618be6-2988-4202-84cf-634ecc976bf2",
    date_added=datetime(2021, 1, 27, 10, 12, 38, 421031),
)
dynamo_teams_user_3: DynamoTeamsUser = DynamoTeamsUser(
    uPN="james@ip-sentinel.com",
    iD="28ad04f7-55d2-4fe8-b917-52f3c24ab13d",
    date_added=datetime(2021, 1, 27, 11, 4, 44, 227297),
)
dynamo_teams_user_4: DynamoTeamsUser = DynamoTeamsUser(
    uPN="denny@ip-sentinel.com",
    iD="0343ab0a-2dee-4672-bc86-20af382ea5d8",
    date_added=datetime(2021, 1, 27, 11, 4, 44, 227297),
)


test_client_1: DynamoClientRecord = DynamoClientRecord(
    client="ips",
    excluded={},
    users=[dynamo_teams_user_1, dynamo_teams_user_2, dynamo_teams_user_3, dynamo_teams_user_4],
)
