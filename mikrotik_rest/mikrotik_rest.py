"""Mikrotik REST API"""

import requests


# Exceptions
class MikrotikRestAPIError(Exception):
    """Mikrotik REST API Error.

    Args:
        Exception (_type_): _description_

    Returns:
        _type_: _description_
    """


# Classes
class MikrotikRest:
    """Mikrotik REST API.

    General docs:
    https://help.mikrotik.com/docs/spaces/ROS/pages/47579162/REST+API

    """
    _api = None
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
            hostname (str): _description_
            username (str): _description_
            password (str): _description_
            timeout (int, optional): _description_. Defaults to 600.
            ssl (bool, optional): _description_. Defaults to False.
            port (int, optional): _description_. Defaults to None.

        Raises:
            RuntimeError: _description_
            EnvironmentError: _description_
            generalUtils.AlreadyExists: _description_

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
            RuntimeError: _description_
            RuntimeError: _description_
            EnvironmentError: _description_
            EnvironmentError: _description_
            EnvironmentError: _description_
            RuntimeError: _description_
            RuntimeError: _description_
            generalUtils.AlreadyExists: _description_
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
            TikRestAPIError: API error.
            # Possibly JSON encoding / decoding error.

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
        if response.status_code not in [200]:
            raise MikrotikRestAPIError(f"Got unknown status code: {response.status_code}")

        return response.json()


    def __call__(self, path: str, method: str = 'GET', oid: str = None, data: dict = None,
                 proplist: list = None, query: list = None) -> dict | list:
        """Call the API.

        Args:
            path (str): _description_
            oid (str, optional): _description_. Defaults to None.
            data (dict, optional): _description_. Defaults to None.
            proplist (list, optional): _description_. Defaults to None.
            query (list, optional): _description_. Defaults to None.

        Returns:
            dict | list: _description_
        """

        data = self._make_request(
            http_method=method,
            url=self._build_url(path),
        )

        return data



if __name__ == '__main__':
    import pprint
    import dotenv

    config  = dotenv.dotenv_values()

    tikh = MikrotikRest(
        config['IP'],
        config['UN'],
        config['PW'],
    )

    # Get all IP addresses
    addresses = tikh("/ip/address")

    print(f"Addresses: {pprint.pformat(addresses)}")

    print("Done")
