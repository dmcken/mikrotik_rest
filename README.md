# Mikrotik REST API handler.


A python handler for the Mikrotik REST API.

## Installation

### From github

```bash
pip install git+https://github.com/dmcken/mikrotik_rest
```

For development with your own local version:

```bash
git clone https://github.com/dmcken/mikrotik_rest.git
cd mikrotik_rest
pip install -e .
```

### From package

To publish at some point...

## Examples

Simple fetch example

```python
# System imports
import pprint

# External imports
import dotenv
import mikrotik_rest

# .env file with IP, username and password
# in appropriate values.
config  = dotenv.dotenv_values()

tikh = MikrotikRest(
    config['IP'],
    config['UN'],
    config['PW'],
)

# Get all IP addresses
addresses = tikh("/ip/address")
pprint.pprint(addresses)

# Get info on the interface ether1
addresses = tikh("/interface",oid='ether1')
```
