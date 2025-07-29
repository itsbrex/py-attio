# list_objects.py

import py_attio

bearer_token = ""

client = py_attio.Client(bearer_token)
objects = client.list_objects()

print(objects)
