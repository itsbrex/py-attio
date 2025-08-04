import unittest
from tests.test_base import BaseTestCase


class TestAttributes(BaseTestCase):
    """Test cases for attributes endpoints."""
    
    def test_list_attributes(self):
        """Test listing attributes for an object."""
        response = self.client.list_attributes('objects', 'people')
        
        # Verify response structure
        self.assertIsInstance(response, dict)
        self.assertIn('data', response)
        self.assertIsInstance(response['data'], list)
        
        # Check for standard attributes
        attribute_slugs = [attr['api_slug'] for attr in response['data']]
        self.assertIn('name', attribute_slugs)
        self.assertIn('email_addresses', attribute_slugs)
    
    def test_get_attribute(self):
        """Test getting a specific attribute."""
        response = self.client.get_attribute('objects', 'people', 'name')
        
        # Verify response structure
        self.assertIsInstance(response, dict)
        self.assertIn('data', response)
        self.assertIn('id', response['data'])
        self.assertIn('api_slug', response['data'])
        self.assertIn('title', response['data'])
        self.assertIn('type', response['data'])
        self.assertEqual(response['data']['api_slug'], 'name')
    
    def test_create_update_delete_attribute(self):
        """Test creating, updating, and deleting a custom attribute."""
        # First create a custom object to add attributes to
        object_name = self.generate_unique_name('attr_object')
        object_payload = {
            "data": {
                "api_slug": object_name,
                "singular_noun": object_name.capitalize(),
                "plural_noun": f"{object_name}s"
            }
        }
        
        object_response = self.client.create_object(payload=object_payload)
        object_id = object_response['data']['id']['object_id']
        self.created_objects.append(object_id)
        
        # Create attribute
        attr_name = self.generate_unique_name('attribute')
        create_payload = {
            "data": {
                "api_slug": attr_name,
                "title": attr_name.replace('_', ' ').title(),
                "type": "text"
            }
        }
        
        create_response = self.client.create_attribute('objects', object_id, payload=create_payload)
        self.assertIn('data', create_response)
        self.assertIn('id', create_response['data'])
        attribute_id = create_response['data']['id']['attribute_id']
        self.created_attributes.append((object_id, attribute_id))
        
        # Update attribute
        update_payload = {
            "data": {
                "title": f"Updated {attr_name}"
            }
        }
        
        update_response = self.client.update_attribute('objects', object_id, attribute_id, payload=update_payload)
        self.assertEqual(update_response['data']['title'], f"Updated {attr_name}")
        
        # Delete attribute
        delete_response = self.client.delete_attribute('objects', object_id, attribute_id)
        self.assertIsInstance(delete_response, dict)
        self.created_attributes.remove((object_id, attribute_id))