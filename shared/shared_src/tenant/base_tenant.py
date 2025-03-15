import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Tenant:
    """
    Date of range execution controls
    Mainly: Because the APIs shoud just be an API client that returns requests.
    """

    @staticmethod
    def date_ranges(start_date=None, end_date=None, default_date_diff: int = 1):
        if args_dates := bool(start_date and end_date):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            if args_dates == end_date < start_date:  # if date range is incorrect
                start_date = (datetime.now() - timedelta(days=default_date_diff)).date()
                end_date = datetime.now().date()
        else:
            start_date = (datetime.now() - timedelta(days=default_date_diff)).date()
            end_date = datetime.now().date()
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
