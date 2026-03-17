import unittest
from tests.test_base import BaseTestCase
from datetime import datetime, timedelta


class TestTasks(BaseTestCase):
    """Test cases for tasks endpoints."""
    
    def test_create_get_update_delete_task(self):
        """Test full CRUD operations on a task."""
        # Create a person to assign the task to (tasks require an assignee)
        person_payload = {
            "data": {
                "values": {
                    "name": [{"first_name": "Task", "last_name": "Assignee"}],
                    "email_addresses": [{"email_address": f"task_{self.generate_unique_name('assignee')}@example.com"}]
                }
            }
        }
        
        try:
            person_response = self.client.create_record('people', payload=person_payload)
        except ValueError as e:
            self.skip_if_contract_mismatch(e, "People record creation for tasks tests")
        person_id = person_response['data']['id']['record_id']
        self.created_records.append(('people', person_id))
        
        # Get workspace members to use as assignee
        members = self.client.list_workspace_members()
        if not members['data']:
            self.skipTest("No workspace members available for task assignment")
        
        assignee_id = members['data'][0]['id']['workspace_member_id']
        
        # Create a task
        deadline = (datetime.now() + timedelta(days=7)).isoformat() + 'Z'
        task_payload = {
            "data": {
                "content": "Test task content",
                "deadline_at": deadline,
                "assignees": [
                    {
                        "workspace_member_id": assignee_id
                    }
                ],
                "linked_records": [
                    {
                        "target_object": "people",
                        "target_record_id": person_id
                    }
                ]
            }
        }
        
        create_response = self.client.create_task(payload=task_payload)
        self.assertIn('data', create_response)
        self.assertIn('id', create_response['data'])
        task_id = create_response['data']['id']['task_id']
        self.created_tasks.append(task_id)
        
        # Get the task
        get_response = self.client.get_task(task_id)
        self.assertEqual(get_response['data']['id']['task_id'], task_id)
        self.assertEqual(get_response['data']['content'], "Test task content")
        
        # Update the task
        update_payload = {
            "data": {
                "content": "Updated task content",
                "is_completed": True
            }
        }
        
        update_response = self.client.update_task(task_id, payload=update_payload)
        self.assertEqual(update_response['data']['content'], "Updated task content")
        self.assertTrue(update_response['data']['is_completed'])
        
        # List tasks
        list_response = self.client.list_tasks()
        self.assertIn('data', list_response)
        task_ids = [task['id']['task_id'] for task in list_response['data']]
        self.assertIn(task_id, task_ids)
        
        # Delete the task
        delete_response = self.client.delete_task(task_id)
        self.assertIsInstance(delete_response, dict)
        self.created_tasks.remove(task_id)
