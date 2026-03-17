import unittest
from tests.test_base import BaseTestCase


class TestWorkspaceMembers(BaseTestCase):
    """Test cases for workspace members endpoints."""
    
    def test_list_workspace_members(self):
        """Test listing workspace members."""
        try:
            response = self.client.list_members()
        except PermissionError as e:
            if "User Management scope" in str(e):
                self.skipTest("API key lacks User Management scope")
            raise
        
        # Verify response structure
        self.assertIsInstance(response, dict)
        self.assertIn('data', response)
        self.assertIsInstance(response['data'], list)
        
        # If there are members, verify structure
        if response['data']:
            member = response['data'][0]
            self.assertIn('id', member)
            self.assertIsInstance(member['id'], dict)
            self.assertIn('workspace_id', member['id'])
            self.assertIn('workspace_member_id', member['id'])
            self.assertIn('email_address', member)
            self.assertIn('created_at', member)
            
    def test_get_workspace_member(self):
        """Test getting a specific workspace member."""
        # First, get list of members to get a valid ID
        try:
            members = self.client.list_members()
        except PermissionError as e:
            if "User Management scope" in str(e):
                self.skipTest("API key lacks User Management scope")
            raise
        
        if members['data']:
            member_id = members['data'][0]['id']['workspace_member_id']
            
            # Get specific member
            response = self.client.get_member(member_id)
            
            # Verify response structure
            self.assertIsInstance(response, dict)
            self.assertIn('data', response)
            self.assertIn('id', response['data'])
            self.assertIsInstance(response['data']['id'], dict)
            self.assertIn('workspace_id', response['data']['id'])
            self.assertIn('workspace_member_id', response['data']['id'])
            self.assertIn('email_address', response['data'])
            self.assertEqual(response['data']['id']['workspace_member_id'], member_id)
