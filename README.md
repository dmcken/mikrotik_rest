# Mikrotik REST API handler.


A python handler for the Mikrotik REST API.

## Installation

### From github

```bash
pip install git+https://github.com/dmcken/mikrotik_rest

or place the following in your requirements.txt

git+https://github.com/dmcken/mikrotik_rest
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

### Search for objects matching specific parameters

These parameters are AND'ed together. So a query for interfaces named lo and mtu of 65536 would look like.

At the moment these are full matches, no regex or similar support exists.

As such no equivalent of `/interface> print where name ~ "ether"` exists (you are going to have to fetch everything and filter yourself).

```python
result = tikh(
    '/interface',
    method='GET',
    query={'name': 'lo','mtu': '65536'},
)
print(f"Count: {len(result)}")
pprint.pprint(result)
```
Output:
```bash
Count: 1
[{'.id': '*C',
  'actual-mtu': '65536',
  'disabled': 'false',
  'fp-rx-byte': '0',
  'fp-rx-packet': '0',
  'fp-tx-byte': '0',
  'fp-tx-packet': '0',
  'last-link-up-time': '2024-09-24 15:53:31',
  'link-downs': '0',
  'mac-address': '00:00:00:00:00:00',
  'mtu': '65536',
  'name': 'lo',
  'running': 'true',
  'rx-byte': '13851160',
  'rx-drop': '0',
  'rx-error': '0',
  'rx-packet': '80530',
  'tx-byte': '13851160',
  'tx-drop': '0',
  'tx-error': '0',
  'tx-packet': '80530',
  'tx-queue-drop': '0',
  'type': 'loopback'}]
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

### Fetch only specific properties
```python
result = tikh(
    '/interface',
    method='GET',
    proplist=['name','mtu','running'],
)
print(f"Count: {len(result)}")
pprint.pprint(result)
```
Output:
```
Count: 11
[{'.id': '*1', 'mtu': '9004', 'name': 'ether1', 'running': 'true'},
 {'.id': '*2', 'mtu': '9004', 'name': 'ether2', 'running': 'false'},
 {'.id': '*3', 'mtu': '9004', 'name': 'ether3', 'running': 'true'},
 {'.id': '*4', 'mtu': '9004', 'name': 'ether4', 'running': 'false'},
 {'.id': '*5', 'mtu': '9004', 'name': 'ether5', 'running': 'false'},
 {'.id': '*6', 'mtu': '9004', 'name': 'ether6', 'running': 'false'},
 {'.id': '*7', 'mtu': '9004', 'name': 'ether7', 'running': 'false'},
 {'.id': '*8', 'mtu': '9004', 'name': 'ether8', 'running': 'false'},
 {'.id': '*9', 'mtu': '9004', 'name': 'sfp-sfpplus1', 'running': 'false'},
 {'.id': '*C', 'mtu': '65536', 'name': 'lo', 'running': 'true'},
 {'.id': '*B', 'mtu': '9004', 'name': 'trunk', 'running': 'true'}]
```

### Set attributes on an object

This uses the add object from above as the oid, you can use either the object returned from a previous add or a fetch to determine this id. You only have to include the information you want to change.

```python
result = tikh(
    '/ip/address',
    method='PATCH',
    oid='*4',
    data={
        'interface': 'ether4',
        'comment': "This was updated using the API",
    }
)

pprint.pprint(result)
```
Output:
```
{'.id': '*4',
 'actual-interface': 'trunk',
 'address': '192.168.56.24/24',
 'comment': 'This was updated using the API',
 'disabled': 'false',
 'dynamic': 'false',
 'interface': 'ether4',
 'invalid': 'false',
 'network': '192.168.56.0',
 'slave': 'true'}
```

### Remove an object

As with the update the oid is acquired via a previous add or fetch.

Officially there is no return value from the API upon success, the success message is generated by this library.

```python
result = tikh(
    '/ip/address',
    method='DELETE',
    oid='*4',
)

pprint.pprint(result)
```
Output:
```bash
{'message': 'Success'}
```

