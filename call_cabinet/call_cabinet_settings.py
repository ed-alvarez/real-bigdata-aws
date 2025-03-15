from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.environ.get("LOGGING_LEVEL", "INFO")


class BaseUrls(Enum):
    """Call Cabinet Base Urls"""

    CALL_CABINET: str = "https://api.callcabinet.com"
    ATMOS_CALL_CABINET: str = "https://atmos.callcabinet.com"
    SECURE_CALL_CABINET: str = "https://secure.callcabinet.com"


class CallCabinetKeys(Enum):
    """Call Cabinet access keys"""

    API_KEY: str = os.getenv("API_KEY")
    CUSTOMER_ID: str = os.getenv("CUSTOMER_ID")
    SITE_ID: str = os.getenv("SITE_ID")
