import json
import logging
from typing import Dict, List, Optional

import requests
from msal import ConfidentialClientApplication

log = logging.getLogger(__name__)
logging.getLogger("msal").setLevel(logging.WARN)
logging.getLogger("urllib3").setLevel(logging.WARN)


class MSALToken:
    def __init__(self, Tenant_ID: str = "", Client_ID: str = "", Secret: str = "") -> None:
        self._tenantId: str = Tenant_ID
        self._clientID: str = Client_ID
        self._secret: str = Secret

        self._authority: str = "https://login.microsoftonline.com/" + self._tenantId
        self._scope: List = list()
        self.__add_to_scope("https://graph.microsoft.com/.default")

        self._access_token: str = ""
        self._http_headers: Dict = dict()
        self._app: ConfidentialClientApplication = self._create_app_instance(
            client_id=self._clientID, authority=self._authority, credentials=self._secret
        )

    @property
    def get_headers(self) -> Dict:
        self.get_token()
        return self._http_headers

    def __add_to_scope(self, Scope_Item: str) -> None:
        self._scope.append(Scope_Item)

    def _create_app_instance(self, client_id: str, authority: str, credentials: str) -> ConfidentialClientApplication:
        app: ConfidentialClientApplication = ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=credentials,
            # token_cache=...  # Default cache is in memory only.
            # You can learn how to use SerializableTokenCache from
            # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
        )
        return app

    def get_token(self) -> None:
        # The pattern to acquire a token looks like this.
        result: Dict = {}

        # Firstly, looks up a token from cache
        # Since we are looking for token for the current app, NOT for an end user,
        # notice we give account parameter as None.
        result = self._app.acquire_token_silent(self._scope, account=None)

        if not result:
            log.debug("No suitable token exists in cache. Let's get a new one from AAD.")
            result = self._app.acquire_token_for_client(scopes=self._scope)
        if "access_token" in result:
            token = result["access_token"]
            self._access_token = token
            log.debug(f"Token adquired {token}")

            self._http_headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

        else:
            log.exception(result.get("error"))
            log.error(result.get("error_description"))
            log.error(result.get("correlation_id"))  # You may need this when reporting a bug
