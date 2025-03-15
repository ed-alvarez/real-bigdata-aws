"""
Put a record to DynamoDB
Check if a record is already in DynamoDB

"""

import boto3
import email_settings
from botocore.exceptions import ClientError


class emailDynamoDB:
    def __init__(self):
        self._db_record = dict()
        self._db_resource = boto3.resource("dynamodb")
        self._db_table = self._db_resource.Table(email_settings.DYNAMO_DB_TABLE)
        self._db_item = dict()
        self._db_key = str()
        self._aws_write_response = None

    @property
    def dbRecord(self):
        return self._db_record

    @dbRecord.setter
    def dbRecord(self, db_record):
        self._db_record = db_record

    @property
    def dbItem(self):
        return self._db_item

    @property
    def dbKey(self):
        return self._db_key

    @dbKey.setter
    def dbKey(self, db_key):
        self._db_key = db_key

    def put_record(self):
        try:
            self._aws_write_response = self._db_table.put_item(
                Item=self._db_record, ConditionExpression="attribute_not_exists(messageId)"
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                error_msg = "ERROR - Record Exists"
                raise Exception(error_msg)
            else:
                raise Exception(e)

    def get_record(self):
        db_key = {"messageId": self._db_key}
        try:
            response = self._db_table.get_item(Key=db_key)
        except ClientError as e:
            print(e.response["Error"]["Message"])
        else:
            self._db_item = response["Item"]


if __name__ == "__main__":
    from email_ingest.email_helpers.helper_ses import processSESEvent
    from email_ingest.email_tests.ses_records import ses_record1

    record = processSESEvent()
    record.event = ses_record1.aws_data_2
    record.parseEvent()

    dynamo = emailDynamoDB()
    dynamo.dbRecord = record.dynamoRec
    dynamo.put_record()

    dynamo.dbKey = "7k822gft4kqtq4dgji1sqdhnqgqnj9bsv76lqoo1"
    dynamo.get_record()
    result = dynamo.dbItem
