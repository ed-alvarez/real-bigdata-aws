from teams_src.teams_shared_modules.teams_data_classes import DynamoClientRecord

try:
    dynamo_client_record: DynamoClientRecord = DynamoClientRecord(client=self._aws_event.tenant_name).get_dynamo_client()
except Exception as ex:
    log.exception("Error loading dynamo record")
    raise ex
