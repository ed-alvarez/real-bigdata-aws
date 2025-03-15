import datetime

from freezegun import freeze_time
from voice_clients_src.valeur.event_decode import EventDecode

event_daily = {"firm": "testing", "type": "daily"}
event_history = {"firm": "testing", "type": "history", "dt_from": "2020-12-30", "dt_to": "2021-01-02"}
FAKE_TIME = datetime.datetime(year=2020, month=12, day=25, hour=17, minute=5, second=55, microsecond=3030)


class TestFunctions:
    def test_datetime_to_directory_format(self):
        test_obj = EventDecode(event=event_history)
        result = test_obj._datetime_to_directory_format(date_dt=FAKE_TIME)
        assert result == "20201225"

    def test_event_date_to_date(self):
        test_obj = EventDecode(event=event_history)
        result: datetime.date = test_obj._event_date_to_date(dt_date=event_history["dt_from"])
        assert result.year == 2020

    def test__generate_date_list_daily(self):
        test_obj = EventDecode(event=event_daily)
        with freeze_time(FAKE_TIME):
            result = test_obj._generate_date_list(dt_from="", dt_to="")
        assert result == ["20201225"]

    def test__generate_date_list_history_short(self):
        test_obj = EventDecode(event=event_history)
        result = test_obj._generate_date_list(dt_from="2021-01-01", dt_to="2021-01-02")
        assert result == ["20210101", "20210102"]

    def test__generate_date_list_history_long(self):
        test_obj = EventDecode(event=event_history)
        result = test_obj._generate_date_list(dt_from="2020-12-30", dt_to="2021-01-02")
        assert result == ["20201230", "20201231", "20210101", "20210102"]

    def test_list_of_dates_daily(self):
        test_obj = EventDecode(event=event_daily)
        with freeze_time(FAKE_TIME):
            result = test_obj.DateList
        assert result == ["20201225"]

    def test_list_of_dates_history(self):
        test_obj = EventDecode(event=event_history)
        result = test_obj.DateList
        assert result == ["20201230", "20201231", "20210101", "20210102"]
