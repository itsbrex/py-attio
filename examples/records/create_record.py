"""Create a record in a target object."""

import os
import py_attio

api_key = os.getenv("ATTIO_API_KEY")
if not api_key:
    raise SystemExit("Set ATTIO_API_KEY before running this example.")

client = py_attio.Client(api_key)

object_slug = "object_slug"
payload = {"data": {"values": {"attribute_slug": ["attribute_value"]}}}

print(client.create_record(object_slug, payload))
