"""
client.py

This module provides the main interface to the Attio API.

It defines the `Client` class, which serves as the public entry point for interacting
with Attio objects, records, views, and workflows. The client handles authentication,
constructs and executes HTTP requests, and exposes resource-specific methods for
working with the Attio API.

The module also includes the internal `BaseClient` class, which implements shared
HTTP functionality and should not be used directly.

Classes:
    Client: Public-facing API client for Attio.
    BaseClient: Internal base class for low-level request handling.

Usage:
    import py_attio

    client = py_attio.Client(token="your_api_token")
    objects = client.list_objects()

    print(objects)
"""

from typing import Dict, Any  # , List, Optional
import requests


class BaseClient:
    """Internal class for interacting with the Attio API"""

    def __init__(self, api_key: str):

        self.base_url = "https://api.attio.com/v2"
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {
                "authorization": f"Bearer {self.api_key}",
                "accept": "application/json",
                "content-type": "application/json",
            }
        )

    def _request(self, method: str, path: str, **kwargs):

        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, **kwargs)
        if not response.ok:
            raise Exception(f"Request failed: {response.status_code} - {response.text}")
        return response.json()


class Client(BaseClient):
    """The main interface to the Attio API"""

    # Objects

    def get_object(self, object_id: str):
        """Gets a single object by its object_id or slug"""
        return self._request("GET", f"/objects/{object_id}")

    def list_objects(self):
        """Lists all system-defined and user-defined objects in the workspace"""
        return self._request("GET", "/objects")

    def create_object(self, payload: Dict[str, Any]):
        """Creates a new custom object in your workspace."""
        return self._request("POST", "/objects", json=payload)

    def update_object(self, object_id: str, payload: Dict[str, Any]):
        """Updates a single object."""
        return self._request("PATCH", f"/objects/{object_id}", json=payload)

    # Attributes

    def list_attributes(self, target: str, identifier: str, query=None):
        """Lists all attributes defined on a specific object or list."""
        if query is None:
            query = {}
        return self._request("GET", f"/{target}/{identifier}/attributes", params=query)

    def create_attribute(self, target: str, identifier: str, payload: Dict[str, Any]):
        """Creates a new attribute on either an object or a list."""
        return self._request("POST", f"/{target}/{identifier}/attributes", json=payload)

    def get_attribute(self, target: str, identifier: str, attribute: str):
        """Gets information about a single attribute on either an object or a list."""
        return self._request("GET", f"/{target}/{identifier}/attributes/{attribute}")

    def update_attribute(
        self, target: str, identifier: str, attribute: str, payload: Dict[str, Any]
    ):
        """Updates a single attribute on a given object or list."""
        return self._request(
            "PATCH", f"/{target}/{identifier}/attributes/{attribute}", json=payload
        )

    # Records

    def list_records(self, object_id: str, payload=None):
        """Lists people, company or other records, with the option to filter and sort results."""
        if payload is None:
            payload = {}
        return self._request(
            "POST", f"/objects/{object_id}/records/query", json=payload
        )

    def get_record(self, object_id: str, record_id: str):
        """Gets a single person, company or other record by its record_id."""
        return self._request("GET", f"/objects/{object_id}/records/{record_id}")

    def create_record(self, object_id: str, payload: Dict[str, Any]):
        """Creates a new person, company or other record."""
        return self._request("POST", f"/objects/{object_id}/records", json=payload)

    def assert_record(self, object_id: str, payload: Dict[str, Any]):
        """Use this endpoint to create or update people, companies and other records."""
        return self._request("PUT", f"/objects/{object_id}/records", json=payload)

    def update_record(self, object_id: str, record_id: str, payload: Dict[str, Any]):
        """Use this endpoint to update people, companies, and other records."""
        return self._request(
            "PUT", f"/objects/{object_id}/records/{record_id}", json=payload
        )

    def delete_record(self, object_id: str, record_id: str):
        """Deletes a single record (e.g. a company or person) by ID."""
        return self._request("DELETE", f"/objects/{object_id}/records/{record_id}")

    def list_record_values(self, object_id: str, record_id: str, attribute: str):
        """Gets all values for a given attribute on a record."""
        return self._request(
            "GET",
            f"/objects/{object_id}/records/{record_id}/attributes/{attribute}/values",
        )

    def list_record_entries(self, object_id: str, record_id: str):
        """List all entries, across all lists, for which this record is the parent."""
        return self._request("GET", f"/objects/{object_id}/records/{record_id}/entries")

    # Lists

    def list_lists(self):
        """List all lists that your access token has access to."""
        return self._request("GET", "/lists")

    def create_list(self, payload: Dict[str, Any]):
        """Creates a new list."""
        return self._request("POST", "/lists", json=payload)

    def get_list(self, list_id: str):
        """Gets a single list in your workspace that your access token has access to."""
        return self._request("GET", f"/lists/{list_id}")

    def update_list(self, list_id: str, payload: Dict[str, Any]):
        """Updates an existing list."""
        return self._request("PATCH", f"/lists/{list_id}", json=payload)

    # Entries

    def list_entries(self, list_id: str, payload=None):
        """Lists entries in a given list, with the option to filter and sort results."""
        if payload is None:
            payload = {}
        return self._request("POST", f"/lists/{list_id}/entries/query", json=payload)

    def create_entry(self, list_id: str, payload: Dict[str, Any]):
        """Adds a record to a list as a new list entry."""
        return self._request("POST", f"/lists/{list_id}/entries", json=payload)

    def assert_entries(self, list_id: str, payload: Dict[str, Any]):
        """Use this endpoint to create or update a list entry for a given parent record."""
        return self._request("PUT", f"/lists/{list_id}/entries", json=payload)

    def get_entry(self, list_id: str, entry_id: str):
        """Gets a single list entry by its entry_id."""
        return self._request("GET", f"/lists/{list_id}/entries/{entry_id}")

    def delete_entry(self, list_id: str, entry_id: str):
        """Deletes a single list entry by its entry_id."""
        return self._request("DELETE", f"/lists/{list_id}/entries/{entry_id}")

    # Workspace members

    def list_members(self):
        """Lists all workspace members in the workspace."""
        return self._request("GET", "/workspace_members")

    def get_member(self, workspace_member_id: str):
        """Gets a single workspace member by ID."""
        return self._request("GET", f"/workspace_members/{workspace_member_id}")

    # Notes

    def list_notes(self, query=None):
        """List notes for all records or for a specific record."""
        if query is None:
            query = {}
        return self._request("GET", "/notes", params=query)

    def create_note(self, payload: Dict[str, Any]):
        """Creates a new note for a given record."""
        return self._request("POST", "/notes", json=payload)

    def get_note(self, note_id: str):
        """Get a single note by ID."""
        return self._request("GET", f"/notes/{note_id}")

    def delete_note(self, note_id: str):
        """Delete a single note by ID."""
        return self._request("DELETE", f"/notes/{note_id}")

    # Tasks

    def list_tasks(self, query=None):
        """List all tasks. Results are sorted by creation date, from oldest to newest."""
        if query is None:
            query = {}
        return self._request("GET", "/tasks", params=query)

    def create_task(self, payload: Dict[str, Any]):
        """Creates a new task."""
        return self._request("POST", "/tasks", json=payload)

    def get_task(self, task_id: str):
        """Get a single task by ID."""
        return self._request("GET", f"/tasks/{task_id}")

    def delete_task(self, task_id: str):
        """Delete a task by ID."""
        return self._request("DELETE", f"/tasks/{task_id}")

    def update_task(self, task_id: str):
        """Updates an existing task by task_id."""
        return self._request("PATCH", f"/tasks/{task_id}")

    # Threads

    def list_threads(self, query: Dict[str, Any]):
        """List threads of comments on a record or list entry."""
        return self._request("GET", "/threads", params=query)

    def get_thread(self, thread_id: str):
        """Get all comments in a thread."""
        return self._request("GET", f"/threads/{thread_id}")

    # Comments

    def create_comment(self, payload: Dict[str, Any]):
        """Creates a new comment related to an existing thread, record or entry."""
        return self._request("POST", "/comments", json=payload)

    def get_comment(self, comment_id: str):
        """Get a single comment by ID."""
        return self._request("GET", f"/comments/{comment_id}")

    def delete_comment(self, comment_id: str):
        """Deletes a comment by ID. If deleting the head of a thread, messages are also deleted."""
        return self._request("DELETE", f"/comments/{comment_id}")

    # Webhooks

    def list_webhooks(self, query=None):
        """Get all of the webhooks in the workspace."""
        if query is None:
            query = {}
        return self._request("GET", "/webhooks", params=query)

    def create_webhook(self, payload: Dict[str, Any]):
        """Create a webhook and associated subscriptions."""
        return self._request("POST", "/webhooks", json=payload)

    def get_webhook(self, webhook_id: str):
        """Get a single webhook."""
        return self._request("GET", f"/webhooks/{webhook_id}")

    def delete_webhook(self, webhook_id: str):
        """Delete a webhook by ID."""
        return self._request("DELETE", f"/webhooks/{webhook_id}")

    def update_webhook(self, webhook_id: str):
        """Update a webhook and associated subscriptions."""
        return self._request("PATCH", f"/webhooks/{webhook_id}")

    # Meta

    def identify_self(self):
        """Identify the current access token, linked workspace, and permissions."""
        return self._request("GET", "/self")
