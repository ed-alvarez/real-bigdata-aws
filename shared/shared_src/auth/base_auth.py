import logging
import os

from dotenv import load_dotenv

load_dotenv()
STAGE = os.environ.get("STAGE", "dev")


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from shared.shared_src.helper_aws_parameters import AWS_Key_Parameters


class BaseAuth:
    def __init__(
        self,
        customer_name,
        api,
    ):
        self.customer_name = customer_name
        self.api = api

        ssm_client = AWS_Key_Parameters(client_name=customer_name)

        self._account_id = os.environ.get(
            f"{api}_account_id",
            ssm_client.get_parameter_value(item_key=f"{api}/account_id"),
        )

        self._client_id = os.environ.get(
            f"{api}_client_id",
            ssm_client.get_parameter_value(item_key=f"{api}/client_id"),
        )

        self._client_secret = os.environ.get(
            f"{api}_client_secret",
            ssm_client.get_parameter_value(item_key=f"{api}/client_secret"),
        )

        self._bearer_cache_location = "/tmp/oauth.json"
        ssm_client = AWS_Key_Parameters(client_name="elastic_app")

        self._url_api_oauth = os.environ.get(
            f"{api}_url_api_oauth",
            ssm_client.get_parameter_value(item_key=f"{STAGE}/{api}/url_api_oauth"),
        )

        self._url_api_token = os.environ.get(
            f"{api}_url_api_token",
            ssm_client.get_parameter_value(item_key=f"{STAGE}/{api}/url_api_token"),
        )

        self._url_api_authorize = os.environ.get(
            f"{api}_url_api_authorize",
            ssm_client.get_parameter_value(item_key=f"{STAGE}/{api}/url_api_authorize"),
        )

        logger.debug(f"LOADING {self} 🚀")

    def __str__(self) -> str:
        return (
            f"Account ID {self._account_id}"
            f"Client ID {self._client_id}"
            f"Client Secret {self._client_secret}"
            f"API OAuth URL {self._url_api_oauth}"
            f"API Token URL {self._url_api_token}"
            f"API Auth URL {self._url_api_authorize} for {self.customer_name} | {self.api}"
        )
