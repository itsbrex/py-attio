# list_notes.py

import py_attio 

bearer_token = ""

client = py_attio.Client(bearer_token)
notes = client.list_notes()

print(notes)
