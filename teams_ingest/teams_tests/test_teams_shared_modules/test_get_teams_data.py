import datetime
import sys
from pathlib import Path

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))

import requests_mock
from freezegun import freeze_time
from teams_src.teams_shared_modules.teams_rest_api.get_teams_data import TeamsDataGrab
from teams_tests.data.get_page_of_data_jhth import http_response

FAKE_TIME = datetime.datetime(year=2020, month=12, day=25, hour=17, minute=5, second=55, microsecond=3030)


class TestTeamsDataGrab:
    def test_constructor(self):
        tdg = TeamsDataGrab()
        assert isinstance(tdg._http_headers, dict)
        assert isinstance(tdg._endpoint, str)
        assert [] == tdg.teamsData

    def test_get_page_of_data(self):
        http_headers = {
            "Authorization": "Bearer random token",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        endpoint = "https://graph.microsoft.com/beta/users/james@ip-sentinel.com"
        with requests_mock.Mocker() as mock:
            mock.get(endpoint, json=http_response)
            tdg = TeamsDataGrab(end_point=endpoint, http_headers=http_headers)
            response = tdg._get_page_of_data(endpoint=endpoint)
            assert response["displayName"] == "James Hogbin"

    def test_construct_date_range_filter(self):
        with freeze_time(FAKE_TIME):
            tdg = TeamsDataGrab()
            result = tdg._construct_date_range_filter()
            assert (
                result
                == "?filter=lastModifiedDateTime gt 2020-12-24T17:05:55.003Z and lastModifiedDateTime lt 2020-12-25T17:05:55.003Z"
            )

    def test_filter_date_string(self):
        tdg = TeamsDataGrab()
        result = tdg._filter_date_string(date_time_obj=FAKE_TIME)
        assert result == "2020-12-25T17:05:55.003Z"

    def test_get_data(self):
        http_headers = {
            "Authorization": "Bearer random token",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        endpoint = "https://graph.microsoft.com/v1.0/users/28ad04f7-55d2-4fe8-b917-52f3c24ab13d/messages?filter=lastModifiedDateTime gt 2021-01-17T11:06:16.797Z and lastModifiedDateTime lt 2021-01-18T11:06:16.797Z"
        with requests_mock.Mocker() as mock:
            mock.get(endpoint, json=http_response)
            tdg = TeamsDataGrab(end_point=endpoint, http_headers=http_headers)
            response = tdg._get_page_of_data(endpoint=endpoint)
            assert response["displayName"] == "James Hogbin"
