"""Model for python GNS3 Connector entity with raw API methods
"""
import requests
from typing import Optional, Any, Dict, Union
from requests import HTTPError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # type: ignore


class Connector:
    """
    Connector to be use for interaction against GNS3 server controller API.

    **Attributes:**

    - `url` (str): URL of the GNS3 server (**required**)
    - `user` (str): User used for authentication
    - `cred` (str): Password used for authentication
    - `verify` (bool): Whether or not to verify SSL
    - `api_version` (int): GNS3 server REST API version
    - `retries (int, optional)`: Retry values to connect. Defaults to 3.
    - `timeout (int, optional)`: Timeout value in secs. Defaults to 5.
    - `proxies (Optional[Dict[str, Any]], optional)`: Proxies dictionary. Optional

    **Returns:**

    `Connector` instance

    **Example:**

    ```python
    >>> server = gns3fy.Connector(url="http://<address>:3080")
    >>> print(server.get_version())
    {'local': False, 'version': '2.2.0b4'}
    ```
    """

    def __init__(
        self,
        url: str,
        user: Optional[str] = None,
        cred: Optional[str] = None,
        verify: bool = False,
        api_version: int = 2,
        retries: int = 3,
        timeout: int = 5,
        proxies: Optional[Dict[str, Any]] = None,
    ):
        # requests.packages.urllib3.disable_warnings()
        self.base_url = f"{url.strip('/')}/v{api_version}"
        self.user = user
        self.cred = cred
        self.headers = {"Content-Type": "application/json"}
        self.verify = verify
        self.api_calls = 0
        self.retries = retries
        self.timeout = timeout
        self.proxies = proxies

        # Create session object
        self._create_session()

    def _create_session(self):
        """
        Creates the requests.Session object and applies the necessary parameters
        """
        self.session = requests.Session()
        self.session.headers["Accept"] = "application/json"
        if self.user:
            self.session.auth = (self.user, self.cred)  # type: ignore
        if self.proxies:
            self.session.proxies.update(self.proxies)

        retry_method = Retry(
            total=self.retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_method)

        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def http_call(
        self,
        method: str,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        verify: bool = False,
        params: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Performs the HTTP operation actioned

        **Required Attributes:**

        - `method` (enum): HTTP method to perform: get, post, put, delete, head,
        patch (**required**)
        - `url` (str): URL target (**required**)
        - `data`: Dictionary or byte of request body data to attach to the Request
        - `json_data`: Dictionary or List of dicts to be passed as JSON object/array
        - `headers`: Dictionary of HTTP Headers to attach to the Request
        - `verify`: SSL Verification
        - `params`: Dictionary or bytes to be sent in the query string for the Request
        """
        if data:
            _request = requests.Request(
                method.upper(),
                url,
                data=data,
                headers=headers,
                params=params,
            )

        elif json_data:
            _request = requests.Request(
                method.upper(),
                url,
                json=json_data,
                headers=headers,
                params=params,
            )

        else:
            _request = requests.Request(
                method.upper(),
                url,
                headers=headers,
                params=params,
            )

        _request = self.session.prepare_request(_request)
        self.api_calls += 1

        try:
            _response = self.session.send(
                request=_request, verify=verify, timeout=self.timeout  # type: ignore
            )
        except Exception as err:
            raise err

        try:
            _response.raise_for_status()
        except HTTPError:
            raise HTTPError(
                f"{_response.json()['status']}: {_response.json()['message']}"
            )
        except Exception as err:
            raise err

        return _response
