import logging
from call_cabinet_settings import BaseUrls, LOG_LEVEL
from utils.requests import make_requests
import datetime


logger = logging.getLogger(__name__)
logging.basicConfig(level=LOG_LEVEL)


class CallCabinetAPI:
    def __init__(
        self,
        api_key: str,
        customer_id: str,
        site_id: str,
        start_date: str = None,
        end_date: str = None,
    ):
        self.api_key = api_key
        self.customer_id = customer_id
        self.site_id = site_id
        self.start_date: str = start_date or (
            datetime.datetime.utcnow() - datetime.timedelta(days=1)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.end_date: str = end_date or datetime.datetime.utcnow().strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        self.call_logs = []
        self.call_ids = []
        self.calls_urls_to_download = []

    def get_all_calls(self) -> list:
        """Get all calls"""

        response = make_requests(
            url=f"{BaseUrls.CALL_CABINET.value}/api/CallListingService",
            method="GET",
            params={
                "APIKey": self.api_key,
                "CustomerID": self.customer_id,
                "SiteID": self.site_id,
                "FromDateTime": self.start_date,
                "ToDateTime": self.end_date,
            },
        )

        return response

    def get_call_recording(self, call_id: str) -> bytes:
        """Download call recording"""

        response = make_requests(
            url=f"{BaseUrls.CALL_CABINET.value}/APIServices/DownloadAudioFile",
            method="GET",
            params={
                "APIKey": self.api_key,
                "CustomerID": self.customer_id,
                "SiteID": self.site_id,
                "CallID": call_id,
            },
        )
        return response


# TODO what if we want to add
# TODO start_date, self.end_date to query with specific time-ranges.
# TODO use the from shared.shared_src.tenant.base_tenant import Tenant
# TODO Tenant.date_ranges and enhance init to be:
# TODO def __init__(self, customer_name: str = "", start_date: str = "", end_date: str = ""):

# TODO where accordingly to the CUSTOMER, then it will use the KEYS of that customer. Let me do example:


"""
callcabinet_client_gemstock = CallCabinetAPI(
    customer_name=gemstock,
    start_date=01-03-2023,
    end_date=02-03-2023,
) *Uses the keys we have (api, customer, site id)


callcabinet_client_iccha = CallCabinetAPI(
    customer_name=iccha
) *Uses ICCHA keys (api, customer, site id)
** beyond, if not start_end date the tenant will do default today()

"""
