import sys
from datetime import datetime
from pathlib import Path
from typing import List

import pytest

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))

from teams_src.teams_data_fetch_conversation import event_date_helper_functions
from teams_src.teams_shared_modules.teams_data_classes import TeamsDateRange
from teams_tests.data.stepfunction_data import teams_history_event


class TestFunction:
    def test_parse_event_for_period(self):
        result: List[TeamsDateRange] = event_date_helper_functions.parse_event_for_period(event=teams_history_event)
        assert len(result) == 2

    def test_generate_date_range(self):
        test_time_1: datetime = datetime(2020, 5, 17)
        test_result_1: TeamsDateRange = TeamsDateRange()
        test_result_1.search_to = datetime(2020, 5, 16, 23, 59, 59, 99999)
        test_result_1.search_from = datetime(2020, 5, 16, 0, 0, 0)

        test_time_2: datetime = datetime(2017, 11, 28, 23, 55, 59, 342380)
        test_result_2: TeamsDateRange = TeamsDateRange()
        test_result_2.search_to = datetime(2017, 11, 27, 23, 59, 59, 99999)
        test_result_2.search_from = datetime(2017, 11, 27, 0, 0, 0)

        CASES = [
            (test_time_1, test_result_1),
            (test_time_2, test_result_2),
        ]

        for input, expected in CASES:
            result: TeamsDateRange = event_date_helper_functions._generate_date_range(date=input)
            assert expected == result

    def test_generate_list_between_two_days(self):
        start_date: datetime = datetime(2020, 5, 17)
        end_date: datetime = datetime(2020, 5, 27)

        result: List[datetime] = event_date_helper_functions._generate_list_between_two_dates(start_date=start_date, end_date=end_date)
        assert len(result) == 11
