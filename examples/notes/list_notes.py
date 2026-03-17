"""List notes visible to the API token."""

import os
import py_attio

api_key = os.getenv("ATTIO_API_KEY")
if not api_key:
    raise SystemExit("Set ATTIO_API_KEY before running this example.")

client = py_attio.Client(api_key)
print(client.list_notes())
