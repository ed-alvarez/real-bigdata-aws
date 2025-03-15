import datetime
from pathlib import Path

from email_helpers.helper_events import EventDetail, PathDetail, pathDetailSES
from email_settings import eventType
from email_tests.ses_records.s3_event import create_event as s3_event
from email_tests.ses_records.ses_event import create_event as ses_event
from email_tests.ses_records.test_event import create_event as lambda_event

BASE_DIR = Path(__file__).resolve().parent.parent


class TestPath:
    def test_ses_event(self):
        # this is what the SES event should provide as the message ID
        file_name = "testmessageid"
        folder_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        path_detail = pathDetailSES()
        path_detail.messageID = file_name
        path_detail.inputBucket = "ips.ips"
        path_detail.eventType = eventType.SES
        path_detail.ses_generate_key()
        path_detail.generate_paths()

        assert path_detail.inputKey == "dev.todo.email/mime/" + file_name
        assert path_detail.processedBucket == "ips.ips"
        assert path_detail.processedKey == "dev.processed.email/" + folder_date + "/mime/" + file_name
        assert path_detail.archivedKey == "dev.archived.email/" + folder_date + "/mime/" + file_name

    def test_s3_event_moved(self):
        folder_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        file_name = "01l55t21r5d74tpftq1o5bl1j9tikqfb44fovc81"
        tests = list()
        test_case = dict()

        # odo.ips.ips/email/
        test_case["bucket"] = "todo.ips.ips"
        test_case["key"] = "email/" + file_name
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + folder_date + "/mime/" + file_name
        tests.append(test_case)

        # stash.ips.ips/email/2016-11-16/
        test_case["bucket"] = "stash.ips.ips"
        test_case["key"] = "email/2016-11-16/" + file_name
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + folder_date + "/mime/" + file_name
        tests.append(test_case)

        # ips.ips/dev.todo.email/mime/
        test_case["bucket"] = "ips.ips"
        test_case["key"] = "dev.todo.email/mime/" + file_name
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + folder_date + "/mime/" + file_name
        tests.append(test_case)

        # ips.ips/dev.processed.email/2020-04-03/mime/
        test_case["bucket"] = "ips.ips"
        test_case["key"] = "dev.processed.email/2020-04-03/mime/" + file_name
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + folder_date + "/mime/" + file_name
        tests.append(test_case)

        for test in tests:
            path_detail = PathDetail()
            path_detail.inputKey = test["key"]
            path_detail.inputBucket = test["bucket"]
            path_detail.eventType = eventType.S3
            path_detail.moveFiles = True
            path_detail.generate_paths()

            assert path_detail.processedBucket == test["ProcessedBucket"]
            assert path_detail.processedKey == test["ProcessedKey"]

    def test_s3_event_not_moved(self):
        folder_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        file_name = "01l55t21r5d74tpftq1o5bl1j9tikqfb44fovc81"
        tests = list()
        test_case = dict()

        # odo.ips.ips/email/
        test_case["bucket"] = "todo.ips.ips"
        test_case["key"] = "email/" + file_name
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + folder_date + "/mime/" + file_name
        tests.append(test_case)

        # stash.ips.ips/email/2016-11-16/
        test_case["bucket"] = "stash.ips.ips"
        test_case["key"] = "email/2016-11-16/" + file_name
        test_case["ProcessedBucket"] = "stash.ips.ips"
        test_case["ProcessedKey"] = "email/2016-11-16/" + file_name
        tests.append(test_case)

        # ips.ips/dev.todo.email/mime/
        test_case["bucket"] = "ips.ips"
        test_case["key"] = "dev.todo.email/mime/" + file_name
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.todo.email/mime/" + file_name
        tests.append(test_case)

        # ips.ips/dev.processed.email/2020-04-03/mime/
        test_case["bucket"] = "ips.ips"
        test_case["key"] = "dev.processed.email/2020-04-03/mime/" + file_name
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/2020-04-03/mime/" + file_name
        tests.append(test_case)

        for test in tests:
            path_detail = PathDetail()
            path_detail.inputKey = test["key"]
            path_detail.inputBucket = test["bucket"]
            path_detail.eventType = eventType.S3
            path_detail.moveFiles = False
            path_detail.generate_paths()

            assert path_detail.processedBucket == test["ProcessedBucket"]
            assert path_detail.processedKey == test["ProcessedKey"]

    def test_s3_event_moved_and_date_changed(self):
        folder_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        change_date = "2016-01-01"
        file_name = "01l55t21r5d74tpftq1o5bl1j9tikqfb44fovc81"
        tests = list()
        test_case = dict()

        # todo.ips.ips/email/
        test_case["bucket"] = "todo.ips.ips"
        test_case["key"] = "email/" + file_name
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + change_date + "/mime/" + file_name
        tests.append(test_case)

        # stash.ips.ips/email/2016-11-16/
        test_case["bucket"] = "stash.ips.ips"
        test_case["key"] = "email/2016-11-16/" + file_name
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + change_date + "/mime/" + file_name
        tests.append(test_case)

        # ips.ips/dev.todo.email/mime/
        test_case["bucket"] = "ips.ips"
        test_case["key"] = "dev.todo.email/mime/" + file_name
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + change_date + "/mime/" + file_name
        tests.append(test_case)

        # ips.ips/dev.processed.email/2020-04-03/mime/
        test_case["bucket"] = "ips.ips"
        test_case["key"] = "dev.processed.email/2020-04-03/mime/" + file_name
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + change_date + "/mime/" + file_name
        tests.append(test_case)

        for test in tests:
            path_detail = PathDetail()
            path_detail.inputKey = test["key"]
            path_detail.inputBucket = test["bucket"]
            path_detail.eventType = eventType.S3
            path_detail.moveFiles = True
            path_detail.generate_paths()
            path_detail.set_path_date_from_email(date_dt=datetime.datetime.strptime(change_date, "%Y-%m-%d"))
            path_detail.construct_paths()

            assert path_detail.processedBucket == test["ProcessedBucket"]
            assert path_detail.processedKey == test["ProcessedKey"]


class TestEvent:
    def test_ses_events(self):
        folder_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        file_name = "01l55t21r5d74tpftq1o5bl1j9tikqfb44fovc81"
        event = ses_event(event_recipient="ips@ip-sentinel.net", event_message_id=file_name, event_subject="fred")
        helper_obj = EventDetail()
        helper_obj.event = event

        assert helper_obj.message_id == file_name
        assert helper_obj.path.processedKey == "dev.processed.email/" + folder_date + "/mime/" + file_name
        assert helper_obj.path.processedBucket == "ips.ips"
        assert helper_obj.client == "ips"
        assert helper_obj.dynamoDB

    def test_s3_events(self):
        folder_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        file_name = "01l55t21r5d74tpftq1o5bl1j9tikqfb44fovc81"
        test_case = dict()
        tests = list()

        # todo.ips.ips/email/
        test_case["event"] = s3_event(event_bucket="todo.ips.ips", event_key="email/" + file_name)
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + folder_date + "/mime/" + file_name
        tests.append(test_case)

        # stash.ips.ips/email/2016-11-16/
        test_case["event"] = s3_event(event_bucket="stash.ips.ips", event_key="email/2016-11-16/" + file_name)
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + folder_date + "/mime/" + file_name
        tests.append(test_case)

        # ips.ips/dev.todo.email/mime/
        test_case["event"] = s3_event(event_bucket="ips.ips", event_key="dev.todo.email/mime/" + file_name)
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + folder_date + "/mime/" + file_name
        tests.append(test_case)

        # ips.ips/dev.processed.email/2020-04-03/mime/
        test_case["event"] = s3_event(event_bucket="ips.ips", event_key="dev.processed.email/2020-04-03/mime/" + file_name)
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + folder_date + "/mime/" + file_name
        tests.append(test_case)

        for test in tests:
            helper_obj = EventDetail()
            helper_obj.event = test["event"]

            assert helper_obj.message_id == file_name
            assert helper_obj.path.processedKey == test["ProcessedKey"]
            assert helper_obj.path.processedBucket == test["ProcessedBucket"]
            assert helper_obj.client == "ips"
            assert not helper_obj.dynamoDB

    def test_lambda_events(self):

        folder_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
        file_name = "01l55t21r5d74tpftq1o5bl1j9tikqfb44fovc81"
        test_case = dict()
        tests = list()

        # todo.ips.ips/email/
        test_case["event"] = lambda_event(event_bucket="todo.ips.ips", event_key="email/" + file_name, move_files=True)
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + folder_date + "/mime/" + file_name
        tests.append(test_case)

        test_case["event"] = lambda_event(event_bucket="todo.ips.ips", event_key="email/" + file_name)
        test_case["ProcessedBucket"] = "todo.ips.ips"
        test_case["ProcessedKey"] = "email/" + file_name
        tests.append(test_case)

        # stash.ips.ips/email/2016-11-16/
        test_case["event"] = lambda_event(event_bucket="stash.ips.ips", event_key="email/2016-11-16/" + file_name)
        test_case["ProcessedBucket"] = "stash.ips.ips"
        test_case["ProcessedKey"] = "email/2016-11-16/" + file_name
        tests.append(test_case)

        # stash.ips.ips/email/2016-11-16/
        test_case["event"] = lambda_event(event_bucket="stash.ips.ips", event_key="email/2016-11-16/" + file_name, move_files=True)
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + folder_date + "/mime/" + file_name
        tests.append(test_case)

        # ips.ips/dev.todo.email/mime/
        test_case["event"] = lambda_event(event_bucket="ips.ips", event_key="dev.todo.email/mime/" + file_name)
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.todo.email/mime/" + file_name
        tests.append(test_case)

        # ips.ips/dev.todo.email/mime/
        test_case["event"] = lambda_event(event_bucket="ips.ips", event_key="dev.todo.email/mime/" + file_name, move_files=True)
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + folder_date + "/mime/" + file_name
        tests.append(test_case)

        # ips.ips/dev.processed.email/2020-04-03/mime/
        test_case["event"] = lambda_event(event_bucket="ips.ips", event_key="dev.processed.email/2020-04-03/mime/" + file_name)

        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/2020-04-03/mime/" + file_name
        tests.append(test_case)

        # ips.ips/dev.processed.email/2020-04-03/mime/
        test_case["event"] = lambda_event(
            event_bucket="ips.ips",
            event_key="dev.processed.email/2020-04-03/mime/" + file_name,
            move_files=True,
        )
        test_case["ProcessedBucket"] = "ips.ips"
        test_case["ProcessedKey"] = "dev.processed.email/" + folder_date + "/mime/" + file_name
        tests.append(test_case)

        for test in tests:
            helper_obj = EventDetail()
            helper_obj.event = test["event"]

            assert helper_obj.message_id == file_name
            assert helper_obj.path.processedKey == test["ProcessedKey"]
            assert helper_obj.path.processedBucket == test["ProcessedBucket"]
            assert helper_obj.client == "ips"
            assert not helper_obj.dynamoDB

    """
    Formats expected on disk
    Old todo.firm.ips
    todo.ips.ips/email/01l55t21r5d74tpftq1o5bl1j9tikqfb44fovc81
    stash.ips.ips/email/2016-11-16/njn5o4pio297hu56iga7lu4tcm2e00a0vtjfdi01

    ips.ips/dev.todo.email/mime/0007o0qlp1vaqe4oic0onrl09qnu70qmjegj23o1
    ips.ips/dev.processed.email/2020-04-03/mime/tljoco51d36kcho3vnm86kolf6cdbki68vekqso1
    """


class TestLiveErrorEvents:
    def json_file_to_dict(self, file_id):

        with open(f"{BASE_DIR}/email_tests/ses_records/{str(file_id)}", "r") as json_file:
            dict_from_file = eval(json_file.read())
        return dict_from_file

    def test_skip_mirabella_subject_skip_processing(self):
        json_file = "mirabella_sync.json"
        event_obj = EventDetail()
        event_obj.event = self.json_file_to_dict(json_file)
        assert event_obj.IngestEmailToES is False

    def test_skip_mirabella_subject_skip_processing(self):
        json_file = "ses_no_subject.json"
        event_obj = EventDetail()
        event_obj.event = self.json_file_to_dict(json_file)
        assert event_obj.IngestEmailToES is True
