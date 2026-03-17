import unittest
from tests.test_base import BaseTestCase


class TestThreadsComments(BaseTestCase):
    """Test cases for threads and comments endpoints."""

    def _get_threads_query(self):
        """Build a valid threads query using an existing record context."""
        try:
            objects = self.client.list_objects().get('data', [])
        except PermissionError as e:
            self.skipTest(f"Cannot discover objects for thread query: {e}")

        for obj in objects:
            object_id = obj.get('id', {}).get('object_id')
            if not object_id:
                continue
            try:
                records = self.client.list_records(object_id, payload={'limit': 1}).get('data', [])
            except PermissionError:
                continue
            if not records:
                continue
            record_id = records[0].get('id', {}).get('record_id')
            if record_id:
                return {'object': object_id, 'record_id': record_id}

        self.skipTest("No accessible records available to query threads")
    
    def test_list_threads(self):
        """Test listing threads."""
        query = self._get_threads_query()
        try:
            response = self.client.list_threads(query)
        except PermissionError as e:
            if "Comments scope" in str(e):
                self.skipTest("API key lacks Comments scope")
            raise
        
        # Verify response structure
        self.assertIsInstance(response, dict)
        self.assertIn('data', response)
        self.assertIsInstance(response['data'], list)
    
    def test_get_thread(self):
        """Test getting a specific thread."""
        query = self._get_threads_query()
        try:
            threads = self.client.list_threads(query)
        except PermissionError as e:
            if "Comments scope" in str(e):
                self.skipTest("API key lacks Comments scope")
            raise
        
        if threads['data']:
            thread_id = threads['data'][0]['id']['thread_id']
            
            # Get specific thread
            response = self.client.get_thread(thread_id)
            
            # Verify response structure
            self.assertIsInstance(response, dict)
            self.assertIn('data', response)
            self.assertIn('id', response['data'])
            self.assertEqual(response['data']['id']['thread_id'], thread_id)
        else:
            self.skipTest("No threads available to test")
    
    def test_create_comment(self):
        """Test creating a comment on a thread."""
        query = self._get_threads_query()
        try:
            threads = self.client.list_threads(query)
        except PermissionError as e:
            if "Comments scope" in str(e):
                self.skipTest("API key lacks Comments scope")
            raise
        
        if not threads['data']:
            self.skipTest("No threads available to comment on")
        
        thread_id = threads['data'][0]['id']['thread_id']
        
        # Create a comment
        comment_payload = {
            "data": {
                "thread_id": thread_id,
                "content": "This is a test comment from the API tests"
            }
        }
        
        response = self.client.create_comment(payload=comment_payload)
        
        # Verify response structure
        self.assertIsInstance(response, dict)
        self.assertIn('data', response)
        self.assertIn('id', response['data'])
        self.assertIn('content', response['data'])
        self.assertEqual(response['data']['content'], "This is a test comment from the API tests")
