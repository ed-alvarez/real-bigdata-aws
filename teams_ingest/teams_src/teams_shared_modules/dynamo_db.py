"""
Put a record to DynamoDB
Check if a record is already in DynamoDB

"""

from dataclasses import asdict
from typing import Any, Dict, List, Optional

import boto3
import teams_settings
from botocore.exceptions import ClientError
from teams_src.teams_shared_modules.teams_data_classes import (
    DynamoClientRecord,
    DynamoTeamsUser,
)


class msTeamsDynamoDB:
    def __init__(self) -> None:
        self._db_user_list: List[Dict] = list(dict())
        self._db_resource: boto3 = boto3.resource("dynamodb")
        self._db_table = self._db_resource.Table(teams_settings.DYNAMO_DB_TABLE)
        self._db_client: str = str()
        self._db_client_record: Optional[DynamoClientRecord] = None
        self._aws_write_response: Optional[Any] = None

    @property
    def dbUserList(self) -> List[DynamoTeamsUser]:
        user_list: List[DynamoTeamsUser] = list()
        for user in self._db_user_list:
            dynamo_user: DynamoTeamsUser = DynamoTeamsUser(**user)
            user_list.append(dynamo_user)
        return user_list

    @dbUserList.setter
    def dbUserList(self, db_user_list: List[DynamoTeamsUser]) -> None:
        user_list_dicts: List[Dict] = list(dict())
        for user in db_user_list:
            user_list_dicts.append(asdict(user))
        self._db_user_list = user_list_dicts

    @property
    def dbClient(self) -> str:
        return self._db_client

    @dbClient.setter
    def dbClient(self, db_client: str) -> None:
        self._db_client = db_client

    def _generate_put_params(self) -> Dict:
        item: Dict = dict()
        item["client"] = self._db_client
        item["users"] = self._db_user_list
        return item

    def _generate_update_expression(self) -> str:
        base_str: str = "set params.uPN=:p"
        return base_str

    def _generate_update_key(self) -> Dict:
        update_key: Dict = dict()
        update_key["client"] = self._db_client
        return update_key

    def _generate_expression_attribute_values(self) -> Dict:
        attribute_values: Dict = dict()
        attribute_values[":p"] = self._db_user_list.uPN
        return attribute_values

    def put_client_record(self) -> None:
        try:
            self._aws_write_response = self._db_table.put_item(
                Item=self._generate_put_params(), ConditionExpression="attribute_not_exists(client)"
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                error_msg = "ERROR - Record Exists"
                raise Exception(error_msg)
            else:
                raise Exception(e)

    def update_params(self) -> None:
        try:
            self._aws_write_response = self._db_table.update_item(
                Key=self._generate_update_key(),
                UpdateExpression=self._generate_update_expression(),
                ExpressionAttributeValues=self._generate_expression_attribute_values(),
                ReturnValues="UPDATED_NEW",
            )
        except ClientError as e:
            raise Exception(e)

    def get_dynamo_client_record(self) -> DynamoClientRecord:
        db_key = {"client": self._db_client}
        try:
            response = self._db_table.get_item(Key=db_key)
        except ClientError as e:
            print(e.response["Error"]["Message"])
        else:
            self._db_client_record = DynamoClientRecord()
        return self._db_client_record


if __name__ == "__main__":

    user_list: List = list()
    user1 = DynamoTeamsUser(uPN="james@ip-sentinel.com")
    user2 = DynamoTeamsUser(uPN="tom@ip-sentinel.com")
    user_list.append(user1)
    user_list.append(user2)

    record = msTeamsDynamoDB()
    record.dbClient = "ips"
    record.dbUserList = user_list
    record.put_client_record()
