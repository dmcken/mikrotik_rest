"""Mikrotik REST API"""
# pylint: disable=logging-fstring-interpolation

# System imports
import logging
import urllib.parse

# External imports
import requests


logger = logging.getLogger("mikrotik_rest")

# Exceptions
class APIError(Exception):
    """Mikrotik REST API Error"""

class ConnectionClosed(Exception):
    """Raised when connection have been closed"""

class EncodingError(Exception):
    """Raised when encoding / decoding fails"""

# Classes
class MikrotikRest:
    """Mikrotik REST API.

    General docs:
    https://help.mikrotik.com/docs/spaces/ROS/pages/47579162/REST+API

    """
    _api = None
    # The API doesn't respect any other value than 60 seconds.
    # https://help.mikrotik.com/docs/spaces/ROS/pages/47579162/REST+API#RESTAPI-Timeout
    _default_timeout = 60
    _ports = {
        'ssl': {
            True: 443,
            False: 80,
        }
    }


    def __init__(self, hostname: str, username: str, password: str,
                 timeout: int = None, ssl: bool=False, port:int = None) -> None:
        """Constructor.

        Args:
            hostname (str): IP or DNS name of mikrotik router.
            username (str): Username to use to login.
            password (str): Password to use to login.
            timeout (int, optional): API timeout. Defaults to None.
            ssl (bool, optional): Use SSL to connect to API. Defaults to False.
            port (int, optional): Port number to connect to API on if non-standard.
                                  Defaults to None.

        Returns:
            None: no return.
        """
        self._ssl = ssl
        self._hostname = hostname
        self._username = username
        self._password = password
        self._auth = None
        if timeout is None:
            timeout = self._default_timeout
        self._timeout = timeout
        if port is None:
            port = self._ports['ssl'][self._ssl]
        self._port = port

    def _build_url(self, section_name: str) -> str:
        """Build the absolute URL from a section name.

        Args:
            section_name (str): Section name (e.g. '/system/resource' or '/ip/address').
                                Must have leading slash.

        Raises:
            RuntimeError: _description_

        Returns:
            str: _description_
        """
        protocol = "https" if self._ssl else "http"
        # If non-standard port set port_spec to ":<port>"
        port_spec = ""
        if self._ports['ssl'][self._ssl] != self._port:
            port_spec = f":{self._port}"

        return f"{protocol}://{self._hostname}{port_spec}/rest{section_name}"

    def _make_request(self, http_method: str, url: str, json_data: dict = None) -> list | dict:
        """Make HTTP request to the API.

        Args:
            http_method (str): HTTP Method (DELETE, GET, PATCH, POST, PUT)
            url (str): URL to request.
            json_data (dict, optional): Associated data to encode to json and add to request.
                                        Defaults to None.

        Raises:
            MikrotikRestAPIError: Error raised from the API itself.
            # Possibly JSON encoding / decoding error. Raise EncodingError

        Returns:
            list | dict: Return data (can be a list or dictionary)
        """
        if self._auth is None:
            self._auth = requests.auth.HTTPBasicAuth(
                self._username,
                self._password,
            )

        response = requests.request(
            method=http_method,
            url=url,
            json=json_data,
            auth=self._auth,
            timeout=self._timeout,
        )

        # GETs return 200 on success
        # PUTs return 201 on success
        # DELETEs return 204 on success
        # Need to handle failures.
        if response.status_code not in [200,201,204]:
            raise APIError(
                f"Got unknown / error status code: {response.status_code}"
            )

        try:
            if http_method == 'DELETE':
                # An empty string is returned for a successful delete
                return_data = {'message': 'Success'}
            else:
                return_data = response.json()
        except requests.exceptions.JSONDecodeError:
            logger.error(f"Unable to parse json: '{response.text}'")
            return_data = response.text

        return return_data


    def __call__(self, path: str, method: str = 'GET', oid: str = None, data: dict = None,
                 proplist: list = None, query: list = None) -> dict | list:
        """Call the API.

        Args:
            path (str): Base path for API call (e.g. /interface or /ip/address).
            oid (str, optional): Object ID (can be *<hex> or unique name like ether1).
                                 Defaults to None.
            data (dict, optional): _description_. Defaults to None.
            proplist (list, optional): _description_. Defaults to None.
            query (list, optional): _description_. Defaults to None.

        Returns:
            dict | list: _description_
        """

        full_url = self._build_url(path)
        if oid is not None:
            full_url += f"/{oid}"

        if proplist is not None:
            # Set up the query parameters to an empty dict if it doesn't exist.
            if query is None:
                query = {}
            query['.proplist'] = ",".join(proplist)

        if query is not None:
            full_url += f"?{urllib.parse.urlencode(query)}"

        logger.error(f"URL: {full_url}")

        data = self._make_request(
            http_method=method,
            url=full_url,
            json_data=data,
        )

        return data


if __name__ == '__main__':
    import pprint
    import dotenv

    config  = dotenv.dotenv_values()

    tikh = MikrotikRest(
        hostname=config['IP'],
        username=config['UN'],
        password=config['PW'],
    )

    # Test code

    result = tikh(
        '/interface',
        method='GET',
        # query={'name': 'lo','mtu': '65536'},
        proplist=['name','mtu','running'],
    )
    print(f"Count: {len(result)}")
    pprint.pprint(result)

    print("Done")
