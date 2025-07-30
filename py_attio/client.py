import requests
from typing import Dict, List, Optional, Any


class BaseClient:

	def __init__(self, api_key: str):

		self.base_url = "https://api.attio.com/v2"
		self.api_key = api_key
		self.session = requests.Session()
		self.session.headers.update({
        	"authorization": f"Bearer {self.api_key}",
        	"accept": "application/json",
        	"content-type": "application/json"
		})


	def _request(self, method: str, path: str, **kwargs):

		url = f"{self.base_url}{path}"
		response = self.session.request(method, url, **kwargs)
		if not response.ok:
			raise Exception(f"Request failed: {response.status_code} - {response.text}")
		return response .json()


class Client(BaseClient):

	# Objects

	def get_object(self, object_id: str):
		return self._request("GET", f"/objects/{object_id}")


	def list_objects(self):
		return self._request("GET", "/objects")


	def create_object(self, payload: Dict[str, Any]):
		return self._request("POST", "/objects", json=payload)


	def update_object(self, object_id: str, payload: Dict[str, Any]):
		return self._request("PATCH", f"/objects/{object_id}", json=payload)


	# Attributes

	def list_attributes(self, target: str, identifier: str):
		return self._request("GET", f"/{target}/{identifier}/attributes")


	def create_attribute(self, target: str, identifier: str, payload: Dict[str, Any]):
		return self._request("POST", f"/{target}/{identifier}/attributes")


	def get_attribute(self, target: str, identifier: str, attribute: str):
		return self._request("GET", f"/{target}/{identifier}/attributes/{attribute}")


	def update_attribute(self, target: str, identifier: str, attribute: str, payload: Dict[str, Any]):
		return self._request("PATCH", f"/{target}/{identifier}/attributes/{attribute}")


	# Records

	def list_records(self, object_id: str, params=None):
		return self._request("POST", f"/objects/{object_id}/records/query", params=params)


	def get_record(self, object_id: str, record_id: str):
		return self._request("GET", f"/objects/{object_id}/records/{record_id}")


	def create_record(self, object_id: str, payload: Dict[str, Any]):
		return self._request("POST", f"/objects/{object_id}/records", json=payload)


	def assert_record(self, object_id: str, payload: Dict[str, Any]):
		return self._request("PUT", f"/objects/{object_id}/records", json=payload)


	# Lists

	def list_lists(self):
		return self._request("GET", "/lists")


	def create_list(self, payload: Dict[str, Any]):
		return self._request("POST", "/lists", json=payload)


	def get_list(self, list_id: str):
		return self._request("GET", f"/lists/{list_id}")


	def update_list(self, list_id: str, payload: Dict[str, Any]):
		return self._request("PATCH", f"/lists/{list_id}", json=payload)


	# Entries

	def list_entries(self, list_id: str):
		return self._request("POST", f"/lists/{list_id}/entries/query")


	def create_entry(self, list_id: str, payload: Dict[str, Any]):
		return self._request("POST", f"/lists/{list_id}/entries", json=payload)


	def assert_entries(self, list_id: str, payload: Dict[str, Any]):
		return self._request("PUT", f"/lists/{list_id}/entries")


	def get_entry(self, list_id: str, entry_id: str):
		return self._request("GET", f"/lists/{list_id}/entries/{entry_id}")


	def delete_entry(self, list_id: str, entry_id: str):
		return self._request("DELETE", f"/lists/{list_id}/entries/{entry_id}")


	# Workspace members

	def list_members(self):
		return self._request("GET", "/workspace_members")


	def get_member(self, workspace_member_id: str):
		return self._request("GET", f"/workspace_members/{workspace_member_id}")


	# Notes

	def list_notes(self):
		return self._request("GET", "/notes")


	def create_note(self, payload: Dict[str, Any]):
		return self._request("POST", "/notes")


	def get_note(self, note_id: str):
		return self._request("GET", f"/notes/{note_id}")


	def delete_note(self, note_id: str):
		return self._request("DELETE", f"/notes/{note_id}")


	# Tasks

	def list_tasks(self):
		return self._request("GET", "/tasks")


	def create_task(self, payload: Dict[str, Any]):
		return self._request("POST", "/tasks", json=payload)


	def get_task(self, task_id: str):
		return self._request("GET", f"/tasks/{task_id}")


	def delete_task(self, task_id: str):
		return self._request("DELETE", f"/tasks/{task_id}") 


	def update_task(self, task_id: str):
		return self._request("PATCH", f"/tasks/{task_id}")


	# Threads

	def list_threads(self, query: Dict[str, Any]):
		return self._request("GET", "/threads", params=query)


	def get_thread(self, thread_id: str):
		return self._request("GET", f"/threads/{thread_id}")


	# Comments

	def create_comment(self, payload: Dict[str, Any]):
		return self._request("POST", "/comments", json=payload)


	def get_comment(self, comment_id: str):
		return self._request("GET", f"/comments/{comment_id}")


	def delete_comment(self, comment_id: str):
		return self._request("DELETE", f"/comments/{comment_id}")


	# Webhooks

	def list_webhooks(self):
		return self._request("GET", "/webhooks")


	def create_webhook(self, payload: Dict[str, Any]):
		return self._request("POST", "/webhooks", json=payload)


	def get_webhook(self, webhook_id: str):
		return self._request("GET", f"/webhooks/{webhook_id}")


	def delete_webhook(self, webhook_id: str):
		return self._request("DELETE", f"/webhooks/{webhook_id}")


	def update_webhook(self, webhook_id: str):
		return self._request("PATCH", f"/webhooks/{webhook_id}")


	# Meta

	def identify_self(self):
		return self._request("GET", "/self")
	
