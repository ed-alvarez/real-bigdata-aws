import logging
from datetime import datetime, timedelta
from typing import ByteString, Dict, List, Optional

import requests

log = logging.getLogger(__name__)
logging.getLogger("msal").setLevel(logging.WARN)
logging.getLogger("urllib3").setLevel(logging.WARN)


class TeamsDataGrab:
    def __init__(self, end_point: str = "", http_headers: Dict = dict()) -> None:
        self._http_headers: Dict = http_headers
        self._endpoint: str = end_point
        self._data: List[Dict] = list(dict())
        self._content: ByteString = bytes()

    @property
    def teamsData(self) -> List[Dict]:
        return self._data

    @property
    def fileContent(self) -> ByteString:
        return self._content

    def _get_page_of_data(self, endpoint: str) -> Dict:
        http_response: Dict = requests.get(endpoint, headers=self._http_headers, stream=False).json()
        return http_response

    def _get_file_data(self, endpoint: str) -> ByteString:
        http_response = requests.get(endpoint, headers=self._http_headers)
        return http_response.content

    def _get_data(self, endpoint: str) -> List[Dict]:
        data: List[Dict] = list(dict())
        http_response: Dict = self._get_page_of_data(endpoint=endpoint)
        if "value" in http_response:
            data = http_response["value"]
            while "@odata.nextLink" in http_response:
                http_response = self._get_page_of_data(endpoint=http_response["@odata.nextLink"])
                data += http_response["value"]
        else:
            log.exception(f"No data found {http_response}")
        return data

    def _filter_date_string(self, date_time_obj: datetime) -> str:
        # 2007-05-07T16:30:00Z
        # date_time_str = datetime.strftime(date_time_obj, '%Y-%m-%dT%H:%M:%S.%fZ')
        date_time_str: str = date_time_obj.isoformat(sep="T")[:-3] + "Z"
        return date_time_str

    def _construct_date_range_filter(
        self,
        dt_start: Optional[datetime] = None,
        dt_end: Optional[datetime] = None,
        time_delta_unit: Optional[str] = None,
        time_delta_number: Optional[int] = None,
    ) -> str:
        "2020-06-04T18:03:11.591Z"
        time_delta_unit: str = "days"
        time_delta_number: int = 1
        dt_end: datetime = dt_end or datetime.now()
        dt_start: datetime = dt_start or dt_end - timedelta(**{time_delta_unit: time_delta_number})
        start_dt_str: str = self._filter_date_string(date_time_obj=dt_start)
        end_dt_str: str = self._filter_date_string(date_time_obj=dt_end)
        filter: str = f"?filter=lastModifiedDateTime gt {start_dt_str} and lastModifiedDateTime lt {end_dt_str}"
        return filter

    def _construct_delta_range_filter(self) -> str:
        dt_today: datetime = datetime.now()
        dt_yesterday: datetime = dt_today - timedelta(days=1)
        start_dt_str: str = self._filter_date_string(date_time_obj=dt_yesterday)
        filter: str = f"?filter=lastModifiedDateTime gt {start_dt_str}"
        return filter

    def get_data_from(self, dt_start: datetime) -> None:
        filter: str = self._construct_date_range_filter(dt_start=dt_start)
        self._data = self._get_data(endpoint=self._endpoint + filter)
        return

    def get_data_history(self, dt_start: datetime, dt_end: datetime):
        filter: str = self._construct_date_range_filter(dt_start=dt_start, dt_end=dt_end)
        self._data = self._get_data(endpoint=self._endpoint + filter)
        return

    def get_data_previous_custom_period(self, time_delta_unit: str, time_delta_number: int) -> None:
        filter: str = self._construct_date_range_filter(time_delta_unit=time_delta_unit, time_delta_number=time_delta_number)
        self._data = self._get_data(endpoint=self._endpoint + filter)
        return

    def get_data_previous_day(self) -> None:
        filter: str = self._construct_date_range_filter()
        self._data = self._get_data(endpoint=self._endpoint + filter)
        return

    def get_data_all(self) -> None:
        self._data = self._get_data(endpoint=self._endpoint)
        return

    def get_single_data(self) -> None:
        self._data.append(self._get_page_of_data(endpoint=self._endpoint))
        return

    def get_delta_last_day_data(self) -> None:
        filter: str = self._construct_delta_range_filter()
        self._data = self._get_data(endpoint=self._endpoint + filter)
        return

    def get_file(self) -> None:
        self._content = self._get_file_data(endpoint=self._endpoint)
        return
