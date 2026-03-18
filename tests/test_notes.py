import unittest
from tests.test_base import BaseTestCase


class TestNotes(BaseTestCase):
    """Test cases for notes endpoints."""
    
    def test_create_get_delete_note(self):
        """Test creating, getting, and deleting a note."""
        self.require_write_access("note create/delete")
        # First create a person to attach the note to
        person_payload = {
            "data": {
                "values": {
                    "name": [{"first_name": "Note", "last_name": "Test"}],
                    "email_addresses": [{"email_address": f"note_{self.generate_unique_name('test')}@example.com"}]
                }
            }
        }
        
        try:
            person_response = self.client.create_record('people', payload=person_payload)
        except ValueError as e:
            self.skip_if_contract_mismatch(e, "People record creation for notes tests")
        person_id = person_response['data']['id']['record_id']
        self.created_records.append(('people', person_id))
        
        # Create a note
        note_payload = {
            "data": {
                "parent_object": "people",
                "parent_record_id": person_id,
                "title": "Test Note",
                "content": "This is a test note content"
            }
        }
        
        create_response = self.client.create_note(payload=note_payload)
        self.assertIn('data', create_response)
        self.assertIn('id', create_response['data'])
        note_id = create_response['data']['id']['note_id']
        self.created_notes.append(note_id)
        
        # Get the note
        get_response = self.client.get_note(note_id)
        self.assertEqual(get_response['data']['id']['note_id'], note_id)
        self.assertEqual(get_response['data']['title'], "Test Note")
        
        # List notes for the parent record
        list_response = self.client.list_notes(query={'parent_object': 'people', 'parent_record_id': person_id})
        self.assertIn('data', list_response)
        note_ids = [note['id']['note_id'] for note in list_response['data']]
        self.assertIn(note_id, note_ids)
        
        # Delete the note
        delete_response = self.client.delete_note(note_id)
        self.assertIsInstance(delete_response, dict)
        self.created_notes.remove(note_id)
