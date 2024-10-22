'''Package init'''
__version__ = "0.0.3"


from .mikrotik_rest import MikrotikRest
from .mikrotik_rest import APIError, ConnectionClosed, EncodingError
