from datetime import datetime

import pytest

from whatsapp_ingest.whatsapp_helpers.helper_objects import (
    newEventDetail,
    newPathDetail,
)
from whatsapp_ingest.whatsapp_settings import S3_BUCKET_PROCESSED
from whatsapp_ingest.whatsapp_tests.events.s3_event import create_event

FAKE_TIME = datetime(year=2020, month=12, day=25, hour=17, minute=5, second=55, microsecond=3030)


@pytest.fixture()
def s3_event():
    yield create_event("ips.ips", "whatsapp/o255h8fqv9jo21q8ug959sqebqvv46fgqqgj23o1", "ad5e55fcc6ac49325e16af52ea63ef7f")


class TestNewPathDetail:
    def test_new_file_path_with_old_date(self):
        message_id = "ad5e55fcc6ac49325e16af52ea63ef7f"
        new_path_obj: newPathDetail = newPathDetail(message_id=message_id)
        new_path_obj.set_date(FAKE_TIME)
        assert new_path_obj.dated_key == "dev.todo.whatsapp/2020-12-25/ad5e55fcc6ac49325e16af52ea63ef7f"

    def test_new_file_path_with_old_date_and_porcessed_files(self):
        message_id = "ad5e55fcc6ac49325e16af52ea63ef7f"
        new_path_obj: newPathDetail = newPathDetail(message_id=message_id)
        new_path_obj.set_date(date_time=FAKE_TIME)
        new_path_obj.set_root_folder(root_folder=S3_BUCKET_PROCESSED)
        assert new_path_obj.dated_key == "dev.processed.whatsapp/2020-12-25/ad5e55fcc6ac49325e16af52ea63ef7f"


class TestNewEventDetail:
    def test_new_event(self, s3_event):
        event_obj: newEventDetail = newEventDetail(event=s3_event)
        assert event_obj.bucket == "ips.ips"
        assert event_obj.message_id == "o255h8fqv9jo21q8ug959sqebqvv46fgqqgj23o1"
