import unittest
import os
from dotenv import load_dotenv
from py_attio import Client
import time
import uuid


class BaseTestCase(unittest.TestCase):
    """Base test case with common setup and teardown for Attio API tests."""
    
    @classmethod
    def setUpClass(cls):
        """Load environment variables and initialize client."""
        load_dotenv()
        api_key = os.getenv('ATTIO_API_KEY')
        if not api_key:
            raise ValueError("ATTIO_API_KEY environment variable not set")
        cls.client = Client(api_key)
        
        # Track resources for cleanup
        cls.created_objects = []
        cls.created_records = []
        cls.created_lists = []
        cls.created_attributes = []
        cls.created_notes = []
        cls.created_tasks = []
        cls.created_webhooks = []
        
    @classmethod
    def tearDownClass(cls):
        """Clean up all created resources."""
        # Clean up in reverse order of dependencies
        
        # Delete webhooks
        for webhook_id in cls.created_webhooks:
            try:
                cls.client.delete_webhook(webhook_id)
            except Exception as e:
                print(f"Failed to delete webhook {webhook_id}: {e}")
        
        # Delete tasks
        for task_id in cls.created_tasks:
            try:
                cls.client.delete_task(task_id)
            except Exception as e:
                print(f"Failed to delete task {task_id}: {e}")
        
        # Delete notes
        for note_id in cls.created_notes:
            try:
                cls.client.delete_note(note_id)
            except Exception as e:
                print(f"Failed to delete note {note_id}: {e}")
        
        # Delete records
        for object_id, record_id in cls.created_records:
            try:
                cls.client.delete_record(object_id, record_id)
            except Exception as e:
                print(f"Failed to delete record {record_id}: {e}")
        
        # Delete lists
        for list_id in cls.created_lists:
            try:
                cls.client.delete_list(list_id)
            except Exception as e:
                print(f"Failed to delete list {list_id}: {e}")
        
        # Delete attributes
        for object_id, attribute_id in cls.created_attributes:
            try:
                cls.client.delete_attribute(object_id, attribute_id)
            except Exception as e:
                print(f"Failed to delete attribute {attribute_id}: {e}")
        
        # Delete objects
        for object_id in cls.created_objects:
            try:
                cls.client.delete_object(object_id)
            except (FileNotFoundError, Exception) as e:
                print(f"Failed to delete object {object_id}: {e}")
    
    def generate_unique_name(self, prefix):
        """Generate a unique name for testing."""
        return f"test_{prefix}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    def assertIsValidUUID(self, value):
        """Assert that a value is a valid UUID."""
        try:
            uuid.UUID(value)
        except ValueError:
            self.fail(f"{value} is not a valid UUID")