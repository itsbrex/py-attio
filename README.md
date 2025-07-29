<h3 align="center">
  <img src="https://raw.githubusercontent.com/benjaminhawn/py-attio/refs/heads/main/assets/py-attio.svg" width="40%">
  <br><br>
  A lightweight Python wrapper for the Attio API.
</h3>


<div align="center">
  <a
    href="https://pypi.org/project/py-attio/"
    target="_blank"
    style="text-decoration:none;"
  >
    <img alt="PyPi" src="https://img.shields.io/pypi/v/py-attio?color=blue" /></a> <!-- here to prevent underscore -->
  <a
    href="https://github.com/benjaminhawn/py-attio/blob/main/LICENSE"
    target="_blank"
    style="text-decoration:none;"
  >
    <img alt="PyPi" src="https://img.shields.io/badge/license-MIT-blue?color=crimson" /></a> <!-- here to prevent underscore -->
</div>


🚀 Installation
---------------
You can install `py-attio` from PyPI using `pip`:

    pip install py-attio


🔧 Usage
--------
#### Example: Retrieving a list of Objects
```
import py_attio

client = py_attio.Client("ATTIO_API_KEY")
objects = client.list_objects()

print(objects)
```

#### Example: Creating a Record
```
import py_attio

client = py_attio.Client("ATTIO_API_KEY")

object = "companies"
payload = {"data": {"values": {"domains": ["example.com"]}}}

client.create_record(object, payload)
```

#### Example: Viewing access token metadata
```
import py_attio

client = py_attio.Client("ATTIO_API_KEY")
print(client.identify_self())
```

⛓ Links
-------
- [Attio API Docs](https://docs.attio.com/rest-api/overview)
