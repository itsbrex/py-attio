import unittest
from tests.test_base import BaseTestCase


class TestRecords(BaseTestCase):
    """Test cases for records endpoints."""
    
    def test_list_records(self):
        """Test listing records for an object."""
        response = self.client.list_records('people')
        
        # Verify response structure
        self.assertIsInstance(response, dict)
        self.assertIn('data', response)
        self.assertIsInstance(response['data'], list)
    
    def test_create_get_update_delete_record(self):
        """Test full CRUD operations on a record."""
        # Create a person record
        create_payload = {
            "data": {
                "values": {
                    "name": [{
                        "first_name": "Test",
                        "last_name": self.generate_unique_name("User")
                    }],
                    "email_addresses": [
                        {
                            "email_address": f"test_{self.generate_unique_name('email')}@example.com"
                        }
                    ]
                }
            }
        }
        
        # Create record
        create_response = self.client.create_record('people', payload=create_payload)
        self.assertIn('data', create_response)
        self.assertIn('id', create_response['data'])
        record_id = create_response['data']['id']['record_id']
        self.created_records.append(('people', record_id))
        
        # Get record
        get_response = self.client.get_record('people', record_id)
        self.assertEqual(get_response['data']['id']['record_id'], record_id)
        
        # Update record
        update_payload = {
            "data": {
                "values": {
                    "name": [{
                        "first_name": "Updated",
                        "last_name": "Name"
                    }]
                }
            }
        }
        
        update_response = self.client.update_record('people', record_id, payload=update_payload)
        self.assertEqual(update_response['data']['values']['name'][0]['first_name'], 'Updated')
        
        # Delete record
        delete_response = self.client.delete_record('people', record_id)
        self.assertIsInstance(delete_response, dict)
        self.created_records.remove(('people', record_id))
    
    def test_query_records(self):
        """Test querying records with filters."""
        # Create a test record first
        test_email = f"query_test_{self.generate_unique_name('email')}@example.com"
        create_payload = {
            "data": {
                "values": {
                    "name": [{"first_name": "Query", "last_name": "Test"}],
                    "email_addresses": [{"email_address": test_email}]
                }
            }
        }
        
        create_response = self.client.create_record('people', payload=create_payload)
        record_id = create_response['data']['id']['record_id']
        self.created_records.append(('people', record_id))
        
        # Query for the record
        query_payload = {
            "filter": {
                "email_addresses": {
                    "email_address": test_email
                }
            }
        }
        
        query_response = self.client.query_records('people', payload=query_payload)
        self.assertIn('data', query_response)
        self.assertTrue(len(query_response['data']) > 0)
        
        # Verify we found our record
        found = False
        for record in query_response['data']:
            if record['id']['record_id'] == record_id:
                found = True
                break
        self.assertTrue(found, "Created record not found in query results")