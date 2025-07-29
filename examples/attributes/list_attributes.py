# list_attributes.py

import py_attio

bearer_token = ""

client = py_attio.Client(bearer_token)
attributes = client.list_attributes(target="objects", identifier="object_slug")

print(attributes)
