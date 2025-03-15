import datetime
from typing import Dict, List


class EventDecode:
    def __init__(self, event: Dict):
        self._event: Dict = event
        self._client: str = self._event["client"]
        self._type: str = self._event["type"]

    @property
    def Client(self) -> str:
        return self._client

    @property
    def DateList(self) -> List:
        dt_from: str = self._event.get("dt_from", "")
        dt_to: str = self._event.get("dt_to", "")
        date_list: List = self._generate_date_list(dt_from=dt_from, dt_to=dt_to)
        return date_list

    def _datetime_to_directory_format(self, date_dt: datetime) -> str:
        return datetime.datetime.strftime(date_dt, "%Y%m%d")

    def _event_date_to_date(self, dt_date: str) -> datetime.date:
        return datetime.datetime.strptime(dt_date, "%Y-%m-%d").date()

    def _generate_date_list(self, dt_from: str, dt_to: str) -> List:
        date_list: List = []
        if self._type == "daily":
            yesterday_date = self._datetime_to_directory_format(date_dt=datetime.datetime.now())
            date_list.append(yesterday_date)
        if self._type == "history":
            dt_from: datetime.date = self._event_date_to_date(dt_date=dt_from)
            dt_to: datetime.date = self._event_date_to_date(dt_date=dt_to)
            date_list = [
                self._datetime_to_directory_format(dt_from + datetime.timedelta(days=x)) for x in range((dt_to - dt_from).days)
            ]
            date_list.append(self._datetime_to_directory_format(dt_to))
        return date_list
