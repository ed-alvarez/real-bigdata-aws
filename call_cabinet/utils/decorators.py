import requests
from requests.adapters import HTTPAdapter, Retry


def request_base_configs():
    def decorator(func):
        def wrapper(*args, **kwargs):

            retries = 3
            backoff_factor = 0.5
            status_codes = (500, 502, 503, 504)

            session = requests.Session()
            retry = Retry(
                total=retries,
                backoff_factor=backoff_factor,
                status_forcelist=status_codes,
            )

            adapter = HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            for attempt in range(retries + 1):
                response = session.request(*args, **kwargs)
                content_type = response.headers.get("Content-Type")

                if response.status_code not in status_codes:
                    if "application/json" in content_type:
                        return response.json()
                    elif "text/html" in content_type:
                        return response.text
                    else:
                        return response.content

            raise requests.exceptions.RetryError(
                f"Request failed after {retries} attempts"
            )

        return wrapper

    return decorator
