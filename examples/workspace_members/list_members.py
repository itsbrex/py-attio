# list_members.py

import py_attio

bearer_token = ""

client = py_attio.Client(bearer_token)
workspace_members = client.list_members()

print(workspace_members)
