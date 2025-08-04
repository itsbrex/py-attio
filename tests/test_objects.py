import unittest
from tests.test_base import BaseTestCase
import time


class TestObjects(BaseTestCase):
    """Test cases for objects endpoints."""
    
    def test_list_objects(self):
        """Test listing all objects."""
        response = self.client.list_objects()
        
        # Verify response structure
        self.assertIsInstance(response, dict)
        self.assertIn('data', response)
        self.assertIsInstance(response['data'], list)
        
        # Check for standard objects
        object_apis = [obj['api_slug'] for obj in response['data']]
        self.assertIn('people', object_apis)
        self.assertIn('companies', object_apis)
    
    def test_get_object(self):
        """Test getting a specific object."""
        # Get the people object
        response = self.client.get_object('people')
        
        # Verify response structure
        self.assertIsInstance(response, dict)
        self.assertIn('data', response)
        self.assertIn('id', response['data'])
        self.assertIn('api_slug', response['data'])
        self.assertIn('singular_noun', response['data'])
        self.assertIn('plural_noun', response['data'])
        self.assertEqual(response['data']['api_slug'], 'people')
    
    def test_create_update_delete_object(self):
        """Test creating, updating, and deleting a custom object."""
        # Create object
        object_name = self.generate_unique_name('object')
        create_payload = {
            "data": {
                "api_slug": object_name,
                "singular_noun": object_name.capitalize(),
                "plural_noun": f"{object_name}s"
            }
        }
        
        create_response = self.client.create_object(payload=create_payload)
        self.assertIn('data', create_response)
        self.assertIn('id', create_response['data'])
        object_id = create_response['data']['id']['object_id']
        self.created_objects.append(object_id)
        
        # Update object
        update_payload = {
            "data": {
                "plural_noun": f"{object_name}_items"
            }
        }
        
        update_response = self.client.update_object(object_id, payload=update_payload)
        self.assertEqual(update_response['data']['plural_noun'], f"{object_name}_items")
        
        # Delete object (cleanup happens in tearDownClass, but we'll remove from tracking)
        try:
            delete_response = self.client.delete_object(object_id)
            self.assertIsInstance(delete_response, dict)
            self.created_objects.remove(object_id)
        except FileNotFoundError:
            # Object deletion might not be supported in current API
            self.created_objects.remove(object_id)
            self.skipTest("Object deletion endpoint not available")