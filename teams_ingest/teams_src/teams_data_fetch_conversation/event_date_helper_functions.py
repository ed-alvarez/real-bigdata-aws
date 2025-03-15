import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_src.teams_shared_modules.step_funtion_data_classes import TeamsEvent
from teams_src.teams_shared_modules.teams_data_classes import TeamsDateRange


def _end_of_day(date_time: datetime) -> datetime:
    return date_time.replace(hour=23, minute=59, second=59, microsecond=99999)


def _start_of_day(date_time: datetime) -> datetime:
    return date_time.replace(hour=0, minute=0, second=0, microsecond=0)


def _generate_date_range(
    date: datetime,
    time_delta_unit: Optional[str] = None,
    time_delta_number: Optional[int] = None,
) -> TeamsDateRange:
    time_delta_unit: str = "days"
    time_delta_number: int = 1

    day_to_process = date - timedelta(**{time_delta_unit: time_delta_number})

    date_range: TeamsDateRange = TeamsDateRange()
    date_range.search_to = _end_of_day(date_time=day_to_process)
    date_range.search_from = _start_of_day(date_time=day_to_process)
    return date_range


def _generate_list_between_two_dates(
    start_date: datetime,
    end_date: datetime,
    time_delta_unit: Optional[str] = None,
    time_delta_number: Optional[int] = None,
) -> List:
    time_delta_unit: str = "days"
    time_delta_number: int = 1

    date_modified: datetime = start_date
    list_of_dates: List = [start_date]

    while date_modified < end_date:
        date_modified += timedelta(**{time_delta_unit: time_delta_number})
        list_of_dates.append(date_modified)

    return list_of_dates


def parse_event_for_period(event: TeamsEvent) -> List[TeamsDateRange]:
    """
    Return a list of date search ranges from and to
    if the period is daily takes time now and remove 1 day
    if the period is history takes from to be 00:00:00 and to be 23:59:59
    """
    dates_to_process: List[TeamsDateRange] = []
    if event.period.lower() == "daily":
        result: TeamsDateRange = _generate_date_range(date=datetime.now())
        dates_to_process.append(result)
    elif event.period.lower() == "historical":
        # Convert date strings to datetime objects
        start_date = datetime.strptime(event.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(event.end_date, "%Y-%m-%d")
        list_of_history_dates = _generate_list_between_two_dates(start_date=start_date, end_date=end_date)
        for history_date in list_of_history_dates:
            teams_date_range: TeamsDateRange = _generate_date_range(date=history_date)
            dates_to_process.append(teams_date_range)

    return dates_to_process
