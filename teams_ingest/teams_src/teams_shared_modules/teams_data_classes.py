# https://medium.com/better-programming/serialisation-and-deserialisation-for-dynamodb-with-python-eaa8f07f08e2
import json
from dataclasses import asdict, field
from datetime import date, datetime
from typing import Dict, List, Optional

import boto3
import pandas
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from botocore.exceptions import ClientError
from marshmallow import EXCLUDE
from marshmallow_dataclass import dataclass
from teams_settings import DYNAMO_DB_TABLE, STAGE


def to_json_shared(data_class_obj):
    result: Dict = asdict(data_class_obj)
    result: str = json.dumps(obj=result, default=myconverter)
    return json.loads(result)


def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()


@dataclass
class TeamsChannels:
    team_name: str
    team_id: str
    channel_list: List[str] = field(default_factory=list)

    def to_json(self):
        return to_json_shared(self)


@dataclass
class TeamsDateRange:
    search_from: datetime = None
    search_to: datetime = None

    def from_str(self):
        return self.search_from.strftime("%Y%m%d")

    def _to_str(self):
        return self.search_to.strftime("%Y%m%d")

    def __str__(self):
        from_ = self.search_from.strftime("%Y-%m-%d-H%M%S")
        to_ = self.search_to.strftime("%Y-%m-%d-H%M%S")
        return f"{from_} to {to_}"

    def get_dates(self):
        from_ = self.search_from.strftime("%Y-%m-%d-H%M%S")
        to_ = self.search_to.strftime("%Y-%m-%d-H%M%S")
        return from_, to_

    def to_json(self):
        return to_json_shared(self)


@dataclass
class DynamoTeamsUser:
    uPN: str = ""
    iD: str = ""
    date_added: datetime = field(default_factory=datetime)

    def __getitem__(self, item):
        return getattr(self, item)

    def to_json(self):
        return to_json_shared(self)


@dataclass
class DynamoClientRecord:

    client: str
    users: List[DynamoTeamsUser] = field(default_factory=lambda: [])
    excluded: set = field(default_factory=set)
    table_name: str = f"{STAGE}-msTeamsIngest"
    ddb_client = boto3.client("dynamodb")

    def get_dynamo_client(self):
        deserializer = TypeDeserializer()
        try:
            # Check if table exists
            self.ddb_client.describe_table(TableName=DYNAMO_DB_TABLE)
        except self.ddb_client.exceptions.ResourceNotFoundException:
            # Table does not exist, create table with schema
            self.create_table_and_schema()

        # Retrieve item with specified key
        try:
            get_result = self.ddb_client.get_item(TableName=DYNAMO_DB_TABLE, Key={"client": {"S": self.client}})
            if self.ddb_client.scan(TableName=DYNAMO_DB_TABLE, Select='COUNT')['Count'] == 0:
                self.create_table_and_schema()
        except self.ddb_client.exceptions.ResourceNotFoundException:
            self.create_table_and_schema()

        # Deserialize item and return
        if get_result.get("Item") is not None:
            deserialised = {k: deserializer.deserialize(v) for k, v in get_result.get("Item").items()}
            return self.Schema().load(deserialised, unknown=EXCLUDE)

    def put_dynamo_client(self):
        deserializer = TypeDeserializer()
        serializer = TypeSerializer()
        try:
            response = self.ddb_client.put_item(
                TableName=DYNAMO_DB_TABLE,
                Item={k: serializer.serialize(v) for k, v in self.Schema().dump(self).items() if v != ""},
            )
        except ClientError as err:
            raise err
        else:
            return response

    def create_table_and_schema(self) -> Dict:
        session = boto3.Session()
        self.ddb_client = session.resource("dynamodb")

        dynamo_table = self.ddb_client.Table(self.table_name)
        dynamo_table.put_item(Item={"client": self.client, "excluded": {""}, "users": []})
        return dynamo_table

    def to_json(self):
        return to_json_shared(self)


@dataclass
class imageURL:
    chat_id: str
    message_id: str
    hosted_contents_id: str
    content: bytes = None

    def to_json(self):
        return to_json_shared(self)


@dataclass
class ClientCreds:
    firm: str
    tenant_id: str
    clientID: Optional[str] = ""
    secret: Optional[str] = ""

    def __post_init__(self):
        ssm = boto3.client("ssm")
        try:
            self.clientID = ssm.get_parameter(Name=f"/teams/{STAGE}/app_id")["Parameter"]["Value"]
        except:
            pass
        try:
            self.secret = ssm.get_parameter(Name=f"/teams/{STAGE}/app_secret", WithDecryption=True)["Parameter"]["Value"]

        except:
            pass

    def to_json(self):
        return to_json_shared(self)


@dataclass
class TeamsTenant:
    firm: str = ""
    tenant_name: str = ""

    def to_json(self):
        return to_json_shared(self)


@dataclass
class TeamsEvent(TeamsTenant):
    tenant_id: str = ""
    period: str = "daily"

    def to_json(self):
        return to_json_shared(self)
