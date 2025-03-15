import logging
import requests
from utils.decorators import request_base_configs

Response = requests.models.Response


@request_base_configs()
def make_requests(
    url, method="GET", params={}, headers={}, body={}
) -> requests.Response:
    """Request module for generic requests"""

    try:
        response: Response = requests(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=body,
        )

    except Exception as error:
        logging.error(error)

    return response
