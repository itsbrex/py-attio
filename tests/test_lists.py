import unittest
from tests.test_base import BaseTestCase


class TestLists(BaseTestCase):
    """Test cases for lists endpoints."""
    
    def test_get_all_lists(self):
        """Test getting all lists."""
        response = self.client.list_lists()
        
        # Verify response structure
        self.assertIsInstance(response, dict)
        self.assertIn('data', response)
        self.assertIsInstance(response['data'], list)
    
    def test_create_get_delete_list(self):
        """Test creating, getting, and deleting a list."""
        # Create a list
        list_name = self.generate_unique_name('list')
        create_payload = {
            "data": {
                "name": list_name,
                "parent_object": ["people"],
                "api_slug": list_name.lower().replace(' ', '_')
            }
        }
        
        try:
            create_response = self.client.create_list(payload=create_payload)
        except ValueError as e:
            self.skip_if_contract_mismatch(e, "List creation")
        self.assertIn('data', create_response)
        self.assertIn('id', create_response['data'])
        list_id = create_response['data']['id']['list_id']
        self.created_lists.append(list_id)
        
        # Get the list
        get_response = self.client.get_list(list_id)
        self.assertEqual(get_response['data']['id']['list_id'], list_id)
        self.assertEqual(get_response['data']['name'], list_name)
        
        # Delete the list
        delete_response = self.client.delete_list(list_id)
        self.assertIsInstance(delete_response, dict)
        self.created_lists.remove(list_id)
    
    def test_list_entries(self):
        """Test managing list entries."""
        # Create a list first
        list_name = self.generate_unique_name('entry_list')
        create_list_payload = {
            "data": {
                "name": list_name,
                "parent_object": ["people"],
                "api_slug": list_name.lower().replace(' ', '_')
            }
        }
        
        try:
            list_response = self.client.create_list(payload=create_list_payload)
        except ValueError as e:
            self.skip_if_contract_mismatch(e, "List creation for entry tests")
        list_id = list_response['data']['id']['list_id']
        self.created_lists.append(list_id)
        
        # Create a person to add to the list
        person_payload = {
            "data": {
                "values": {
                    "name": [{"first_name": "List", "last_name": "Entry"}],
                    "email_addresses": [{"email_address": f"list_{self.generate_unique_name('entry')}@example.com"}]
                }
            }
        }
        
        try:
            person_response = self.client.create_record('people', payload=person_payload)
        except ValueError as e:
            self.skip_if_contract_mismatch(e, "Person creation for list entry tests")
        person_id = person_response['data']['id']['record_id']
        self.created_records.append(('people', person_id))
        
        # Add person to list
        add_entry_payload = {
            "data": {
                "entries": [
                    {
                        "target": {
                            "object": "people",
                            "record_id": person_id
                        }
                    }
                ]
            }
        }
        
        add_response = self.client.create_entry(list_id, payload=add_entry_payload)
        self.assertIn('data', add_response)
        
        # List entries
        entries_response = self.client.list_entries(list_id)
        self.assertIn('data', entries_response)
        self.assertTrue(len(entries_response['data']) > 0)
        
        # Find our entry
        entry_id = None
        for entry in entries_response['data']:
            if entry['record_id'] == person_id:
                entry_id = entry['entry_id']
                break
        
        self.assertIsNotNone(entry_id, "Created entry not found in list")
        
        # Delete entry
        delete_entry_response = self.client.delete_entry(list_id, entry_id)
        self.assertIsInstance(delete_entry_response, dict)
