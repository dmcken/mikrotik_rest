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

### Connect (provides the `tikh` used in other examples)

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
    hostname=config['IP'],
    username=config['UN'],
    password=config['PW'],
)
```

### Fetch all example:
```python
# Get all IP addresses
addresses = tikh("/ip/address")
pprint.pprint(addresses)
```
Output (list of dictionaries):
```bash
Addresses:
[{'.id': '*2',
  'actual-interface': 'trunk',
  'address': '192.168.1.12/24',
  'disabled': 'false',
  'dynamic': 'true',
  'interface': 'trunk',
  'invalid': 'false',
  'network': '192.168.1.0',
  'slave': 'false'}]
```


### Fetch info on specific named entity

This uses the ID field per the mikrotik docs, this can be either the .id field or a unique field for that object (e.g. name for an interface).

```python
interfaces = tikh("/interface",oid='ether1')

print(f"Interface:\n{pprint.pformat(interfaces)}")
```

Output (returns single dictionary):

```
Interface:
{'.id': '*1',
 'actual-mtu': '9004',
 'default-name': 'ether1',
 'disabled': 'false',
 'fp-rx-byte': '742558639',
 'fp-rx-packet': '5912458',
 'fp-tx-byte': '641172',
 'fp-tx-packet': '870',
 'l2mtu': '9192',
 'last-link-down-time': '2024-10-04 13:43:06',
 'last-link-up-time': '2024-10-04 13:43:08',
 'link-downs': '9',
 'mac-address': '78:9A:18:7D:1A:29',
 'max-l2mtu': '9796',
 'mtu': '9004',
 'name': 'ether1',
 'running': 'true',
 'rx-byte': '2208439930351',
 'rx-packet': '1539776076',
 'slave': 'true',
 'tx-byte': '836294118393',
 'tx-packet': '666266211',
 'tx-queue-drop': '0',
 'type': 'ether'}
```

### Add an IP address (raw version)

To get a list of available parameters that can be used in the data object go to the path and add "add" and then hit tab e.g:

```bash
/ip/address/add <tab>
address     comment     copy-from     disabled     interface     network
```

Check the mikrotik docs for what they mean and acceptable values.

```python
result = tikh(
    '/ip/address',
    method='PUT',
    data={
        'interface': 'ether2',
        'address': '192.168.56.24/24',
    }
)

pprint.pprint(result)
```

Output:

The created object (including its ID) is returned.

```
{'.id': '*4',
 'actual-interface': 'ether2',
 'address': '192.168.56.24/24',
 'disabled': 'false',
 'dynamic': 'false',
 'interface': 'ether2',
 'invalid': 'false',
 'network': '192.168.56.0',
 'slave': 'false'}
```



