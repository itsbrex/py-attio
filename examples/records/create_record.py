# create_records.py

import py_attio

bearer_token = ""
client = py_attio.Client("ATTIO_API_KEY")

object = "object_slug"
payload = {"data": {"values": {"attribute_slug": ["attribute_value"]}}}

client.create_record(object, payload)
