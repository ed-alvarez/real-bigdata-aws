import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict

import requests
from requests.adapters import HTTPAdapter, Retry
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError, HTTPError

from shared.shared_src.auth.base_auth import BaseAuth

Response = requests.models.Response


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class OAuth2(BaseAuth):
    """
    According to customer_name point to different:
        clientID & clientSecret & AccountID

    According to API use the
        request_url_token

    For server side token generation:
        With customer credentials _request_token method will be used

    """

    def __init__(self, customer_name):
        super(OAuth2, self).__init__(
            customer_name,
            self._api,
        )
        self.token: str = ""
        self._default_headers: dict = {}
        self._request_token()

    @staticmethod
    def create_qparams(params: dict = {}):
        query_string = ""
        for key, value in params.items():
            query_string = f"{query_string}&{key}={value}"
        return query_string

    def _request_token(self, params: dict = {}) -> Response:
        """
        Request token from server side without pre-authorization.
        :params: token api request parameters, based on customer
        :return: requests post response object
        """
        response: dict = {}
        default_params: dict = {"grant_type": "account_credentials"}

        if params is not None:
            default_params = {**default_params, **params}

        query_params: str = self.create_qparams(default_params)

        url: str = f"{self._url_api_token}?account_id={self._account_id}{query_params}"

        try:
            session = requests.Session()
            retry = Retry(connect=5, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            auth = HTTPBasicAuth(self._client_id, self._client_secret)
            response: Response = session.post(url=url, auth=auth)
            self._cache_token(response)

        except HTTPError:
            http_error = HTTPError.response
            error_msg: str = f"HTTP Request Fail {http_error.reason}, \
                                        {http_error.content} |  {http_error.code}"
            logger.error(error_msg)

        except ConnectionError as conn_error:
            error_msg: str = f"Connection Error {conn_error}"
            logger.error(error_msg)

        except Exception as err:
            error_msg: str = f"Error retrieving {self._api} token {err}"
            logger.error(error_msg)

    def _cache_token(self, token_response: Response) -> str:
        """
        Request and Post process after generating token.

        :param token: token request response object.
        :return: processed token with metadata
            {
              "access_token": "",
              "token_type": "bearer",
              "refresh_token": "",
              "expires_in": 3599,
              "scope": "user:read:admin"
            }
        """
        access_token_dict: Dict = {}

        try:

            access_token_dict: dict = token_response.json()
            expiration_time: str = access_token_dict["expires_in"]
            expiration_time = datetime.now(timezone.utc) + timedelta(seconds=expiration_time)
            access_token_dict["expiration_time"] = int(expiration_time.timestamp())

        except KeyError as error:
            error_msg: str = f"The token has an unexpected keys {error}"
            logger.error(error_msg)

        with open(self._bearer_cache_location, "w") as outfile:
            json.dump(access_token_dict, outfile)

        self.token: str = access_token_dict["access_token"]

    def get_headers(self) -> Dict:
        """
        Used to get default headers with Authorization token to make actual API requests.

        :return: {
                "Authorization": "Bearer ..."
            }
        """

        access_token_dict: Dict

        if os.path.exists(self._bearer_cache_location):  # Read cached token
            with open(self._bearer_cache_location, "r") as infile:
                access_token_dict = json.load(infile)

            time_now: int = int(datetime.now(timezone.utc).timestamp())

            if time_now > access_token_dict["expiration_time"]:
                access_token_dict = self._request_token()
        else:
            access_token_dict = self._request_token()

        self.token: str = access_token_dict["access_token"]
        logger.debug(f"TOKEN: {self.token}")

        self._default_headers = {"Authorization": f"Bearer {self.token}"}
        return self._default_headers
