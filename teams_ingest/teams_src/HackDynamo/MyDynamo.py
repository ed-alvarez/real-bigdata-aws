import boto3


class InnerDynamo:
    def __init__(self):
        self.inner_ddb = boto3.client("dynamodb")

    def list_all_tables(self):
        return self.inner_ddb.list_tables()


class MyDynamo:

    def __init__(self, dynamo_client=None):
        self.ddb = dynamo_client or boto3.client("dynamodb")
        self.inner = InnerDynamo()

    def list_all_tables(self):
        return self.ddb.list_tables()

    def list_all_tables_from_inner(self):
        return self.inner.list_all_tables()