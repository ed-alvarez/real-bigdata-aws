from datetime import datetime, timedelta

from elasticsearch import exceptions

from bbg_ingest.bbg_src.ib_upload_lambda import ib_upload

# bbg_files = {}
# bbg_files["ATT_file_found"] = True
# bbg_files["MSG_file_found"] = True
# bbg_files["IB_file_found"] = True
# bbg_files["MSG_file_name"] = "f902504.msg.190603.xml"
# bbg_files["MSG_XML_to_process"] = True
# bbg_files["MSG_XML_record_number"] = 0
# bbg_files["IB_file_name"] = "f902504.ib.190603.xml"
# bbg_files["IB_XML_to_process"] = True
# bbg_files["IB_XML_to_record_number"] = 0
# bbg_files["ATT_file_name"] = "f902504.att.190603.tar.gz"
#
# event={}
# event['client_name'] = 'test'
# event['file_to_process'] = 'todo.bbg/2019-06-03/f902504.ib.190603.xml'
# event['attachments_file'] = 'todo.bbg/2019-06-03/f902504.att.190603.tar.gz'
#
# event['bbg_files'] = bbg_files
#
# event['xml_record_number'] = '0'


bbg_files = {}
bbg_files["ATT_file_found"] = True
bbg_files["MSG_file_found"] = False
bbg_files["IB_file_found"] = True
bbg_files["ATT_file_name"] = "dev.todo.bbg/2020-06-17/decoded/f944653.att.200617.tar.gz"
bbg_files["MSG_file_name"] = ""
bbg_files["MSG_XML_to_process"] = False
bbg_files["IB_file_name"] = "dev.todo.bbg/2020-06-17/decoded/f944653.ib.200617.xml"
bbg_files["IB_XML_to_process"] = True
bbg_files["IB_XML_to_record_number"] = 0

event = {}
event["file_to_process"] = "dev.todo.bbg/2020-06-17/decoded/f944653.ib.200617.xml"
event["xml_record_number"] = 0
event["attachments_file"] = "dev.todo.bbg/2020-06-17/decoded/f944653.att.200617.tar.gz"
event["client_name"] = "markerinv"
event["bbg_files"] = bbg_files


class TestLambdaContext:
    def __init__(self, time_limit_in_seconds=120):
        self.log_group_name = "local_test_log_group_name"
        self.log_stream_name = "local_test_log_stream_name"
        self.aws_request_id = "local_test_aws_request_id"

        self.start_time = datetime.now()
        self.time_limit_in_seconds = time_limit_in_seconds
        self.end_time = self.start_time + timedelta(seconds=self.time_limit_in_seconds)

    def get_remaining_time_in_millis(self):
        time_now = datetime.now()
        if time_now <= self.end_time:
            time_left = self.end_time - time_now
            time_left_milli = (time_left.seconds * 1000) + (time_left.microseconds / 1000)
        else:
            time_left_milli = 3600000
        return int(time_left_milli)


context = TestLambdaContext()
try:
    ib_upload.lambda_handler(event, context)
except exceptions.ElasticsearchException as ex:
    raise ex
