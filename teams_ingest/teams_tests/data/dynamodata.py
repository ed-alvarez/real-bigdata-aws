from datetime import datetime
from pprint import pprint

from teams_src.teams_shared_modules.teams_data_classes import (
    DynamoClientRecord,
    DynamoTeamsUser,
)


def intial_set():
    client_record = DynamoClientRecord(client="ips")
    client_record.excluded.add("chris@ip-sentinel.com")
    client_record.excluded.add("svc-jira@ip-sentinel.com")
    client_record.excluded.add("ipsentinel@ip-sentinel.com")
    client_record.excluded.add("support@fingerprint-supervision.com")
    client_record.excluded.add("dan@ip-sentinel.com")
    client_record.excluded.add("steve@fingerprint-supervision.com")
    client_record.excluded.add("filereader@ip-sentinel.com")
    client_record.excluded.add("filewriter@ip-sentinel.com")
    response = client_record.put_dynamo_client()
    pprint(response)


def update_users():
    client_record = DynamoClientRecord(client="ips").get_dynamo_client()
    user1 = DynamoTeamsUser(uPN="james@ip-sentinel.com", iD="xxxyyy", date_added=datetime.now())
    user2 = DynamoTeamsUser(uPN="tom@ip-sentinel.com", iD="aaaabbbb", date_added=datetime.now())
    client_record.users.append(user1)
    client_record.users.append(user2)
    response = client_record.put_dynamo_client()
    pprint(response)


intial_set()
