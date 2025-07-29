# list_lists.py

import py_attio

bearer_token = ""

client = py_attio.Client(bearer_token)
lists = client.list_lists()

print(lists)
