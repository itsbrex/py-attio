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
You can install `py-attio` from PyPI using `uv`:

    uv add py-attio

For local development in this repository:

    uv sync --group dev

Run convenience commands with `uv run`:

    uv run list_objects
    uv run associate_single_company_people_locations --help
    uv run test -q


🔧 Usage
--------
#### Example: Retrieving a list of Objects
```
import os
import py_attio

api_key = os.getenv("ATTIO_API_KEY")
client = py_attio.Client(api_key)
objects = client.list_objects()

print(objects)
```

#### Example: Creating a Record
```
import os
import py_attio

api_key = os.getenv("ATTIO_API_KEY")
client = py_attio.Client(api_key)

object_slug = "companies"
payload = {"data": {"values": {"domains": ["example.com"]}}}

client.create_record(object_slug, payload)
```

#### Example: Viewing access token metadata
```
import os
import py_attio

api_key = os.getenv("ATTIO_API_KEY")
client = py_attio.Client(api_key)
print(client.identify_self())
```

🧪 Testing
----------
Run tests with:

    uv run test -q

Integration tests are workspace-dependent. Some tests are intentionally skipped when:
- your API key lacks required scopes (for example, comments or user-management),
- or your workspace schema/API contract does not support specific create payloads.

Detailed test guidance: [docs/testing.md](docs/testing.md)

⛓ Links
-------
- [Attio API Docs](https://docs.attio.com/rest-api/overview)
