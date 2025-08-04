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

from typing import Dict, Any, Optional, Generator
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
            self._handle_error(response)
        return response.json()

    def _handle_error(self, response):
        """Enhanced error handling with specific HTTP status codes."""
        status_code = response.status_code
        try:
            error_data = response.json()
            error_message = error_data.get('message', response.text)
        except:
            error_message = response.text

        if status_code == 400:
            raise ValueError(f"Bad Request (400): {error_message}")
        elif status_code == 401:
            raise PermissionError(f"Unauthorized (401): Invalid API key or permissions - {error_message}")
        elif status_code == 403:
            raise PermissionError(f"Forbidden (403): Access denied - {error_message}")
        elif status_code == 404:
            raise FileNotFoundError(f"Not Found (404): Resource not found - {error_message}")
        elif status_code == 409:
            raise ValueError(f"Conflict (409): Resource conflict - {error_message}")
        elif status_code == 422:
            raise ValueError(f"Unprocessable Entity (422): Validation error - {error_message}")
        elif status_code == 429:
            raise RuntimeError(f"Rate Limited (429): Too many requests - {error_message}")
        elif status_code >= 500:
            raise RuntimeError(f"Server Error ({status_code}): {error_message}")
        else:
            raise Exception(f"Request failed ({status_code}): {error_message}")


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

    def delete_object(self, object_id: str):
        """Deletes a single object by its object_id or slug."""
        return self._request("DELETE", f"/objects/{object_id}")

    # Custom Object Helper Methods
    
    def list_custom_objects(self):
        """Lists only user-defined (custom) objects in the workspace."""
        objects = self.list_objects()
        # Filter for custom objects (those that are not system-defined)
        if 'data' in objects:
            custom_objects = [obj for obj in objects['data'] if obj.get('is_system') is False]
            return {'data': custom_objects}
        return objects

    def get_object_schema(self, object_id: str):
        """Gets the complete schema for an object including all attributes."""
        object_data = self.get_object(object_id)
        if object_data and 'data' in object_data:
            # Get attributes for this object
            attributes = self.list_attributes('objects', object_id)
            if 'data' in object_data:
                object_data['data']['attributes'] = attributes.get('data', [])
        return object_data

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

    def delete_attribute(self, target: str, identifier: str, attribute: str):
        """Deletes a single attribute on a given object or list."""
        return self._request("DELETE", f"/{target}/{identifier}/attributes/{attribute}")

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
        """Updates a single person, company or other record by its record_id."""
        return self._request("PATCH", f"/objects/{object_id}/records/{record_id}", json=payload)

    def delete_record(self, object_id: str, record_id: str):
        """Deletes a single person, company or other record by its record_id."""
        return self._request("DELETE", f"/objects/{object_id}/records/{record_id}")

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

    def delete_list(self, list_id: str):
        """Deletes a single list by its list_id."""
        return self._request("DELETE", f"/lists/{list_id}")

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

    def update_note(self, note_id: str, payload: Dict[str, Any]):
        """Updates a single note by ID."""
        return self._request("PATCH", f"/notes/{note_id}", json=payload)

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

    def update_task(self, task_id: str, payload: Dict[str, Any]):
        """Updates an existing task by task_id."""
        return self._request("PATCH", f"/tasks/{task_id}", json=payload)

    # Threads

    def list_threads(self, query: Dict[str, Any]):
        """List threads of comments on a record or list entry."""
        return self._request("GET", "/threads", params=query)

    def get_thread(self, thread_id: str):
        """Get all comments in a thread."""
        return self._request("GET", f"/threads/{thread_id}")

    def create_thread(self, payload: Dict[str, Any]):
        """Creates a new thread."""
        return self._request("POST", "/threads", json=payload)

    def update_thread(self, thread_id: str, payload: Dict[str, Any]):
        """Updates an existing thread by thread_id."""
        return self._request("PATCH", f"/threads/{thread_id}", json=payload)

    def delete_thread(self, thread_id: str):
        """Deletes a thread by ID."""
        return self._request("DELETE", f"/threads/{thread_id}")

    # Comments

    def create_comment(self, payload: Dict[str, Any]):
        """Creates a new comment related to an existing thread, record or entry."""
        return self._request("POST", "/comments", json=payload)

    def get_comment(self, comment_id: str):
        """Get a single comment by ID."""
        return self._request("GET", f"/comments/{comment_id}")

    def update_comment(self, comment_id: str, payload: Dict[str, Any]):
        """Updates a single comment by ID."""
        return self._request("PATCH", f"/comments/{comment_id}", json=payload)

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

    def update_webhook(self, webhook_id: str, payload: Dict[str, Any]):
        """Update a webhook and associated subscriptions."""
        return self._request("PATCH", f"/webhooks/{webhook_id}", json=payload)

    # Meta

    def identify_self(self):
        """Identify the current access token, linked workspace, and permissions."""
        return self._request("GET", "/self")

    # Pagination and Batch Helper Methods

    def paginate_records(self, object_id: str, payload: Optional[Dict[str, Any]] = None, 
                        page_size: int = 100) -> Generator[Dict[str, Any], None, None]:
        """
        Generator that automatically handles pagination for record queries.
        
        Args:
            object_id: The object to query records for
            payload: Query parameters for filtering/sorting
            page_size: Number of records per page (default: 100)
            
        Yields:
            Individual records from all pages
        """
        if payload is None:
            payload = {}
        
        # Set initial pagination parameters
        payload.setdefault('limit', page_size)
        offset = payload.get('offset', 0)
        
        while True:
            payload['offset'] = offset
            response = self.list_records(object_id, payload)
            
            if 'data' not in response:
                break
                
            records = response['data']
            if not records:
                break
                
            for record in records:
                yield record
                
            # Check if we have more records
            if len(records) < page_size:
                break
                
            offset += page_size

    def paginate_entries(self, list_id: str, payload: Optional[Dict[str, Any]] = None,
                        page_size: int = 100) -> Generator[Dict[str, Any], None, None]:
        """
        Generator that automatically handles pagination for list entry queries.
        
        Args:
            list_id: The list to query entries for
            payload: Query parameters for filtering/sorting
            page_size: Number of entries per page (default: 100)
            
        Yields:
            Individual entries from all pages
        """
        if payload is None:
            payload = {}
            
        # Set initial pagination parameters
        payload.setdefault('limit', page_size)
        offset = payload.get('offset', 0)
        
        while True:
            payload['offset'] = offset
            response = self.list_entries(list_id, payload)
            
            if 'data' not in response:
                break
                
            entries = response['data']
            if not entries:
                break
                
            for entry in entries:
                yield entry
                
            # Check if we have more entries
            if len(entries) < page_size:
                break
                
            offset += page_size

    def batch_create_records(self, object_id: str, records: list, batch_size: int = 50) -> list:
        """
        Create multiple records in batches to avoid rate limits.
        
        Args:
            object_id: The object to create records for
            records: List of record payloads to create
            batch_size: Number of records to create per batch (default: 50)
            
        Returns:
            List of created record responses
        """
        results = []
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            for record_payload in batch:
                try:
                    result = self.create_record(object_id, record_payload)
                    results.append(result)
                except Exception as e:
                    # Include error information in results
                    results.append({'error': str(e), 'payload': record_payload})
        return results
