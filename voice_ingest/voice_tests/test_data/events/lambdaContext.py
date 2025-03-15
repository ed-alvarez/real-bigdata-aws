from datetime import datetime, timedelta


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
            time_left_milli = 0
        return int(time_left_milli)
