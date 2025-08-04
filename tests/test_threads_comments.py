import unittest
from tests.test_base import BaseTestCase


class TestThreadsComments(BaseTestCase):
    """Test cases for threads and comments endpoints."""
    
    def test_list_threads(self):
        """Test listing threads."""
        # List threads (may be empty)
        try:
            response = self.client.list_threads({})
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
        # First check if any threads exist
        try:
            threads = self.client.list_threads({})
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
        # Get an existing thread or skip test
        try:
            threads = self.client.list_threads({})
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