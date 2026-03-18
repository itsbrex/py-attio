import unittest
from tests.test_base import BaseTestCase


class TestWebhooks(BaseTestCase):
    """Test cases for webhooks endpoints."""
    
    def test_list_webhooks(self):
        """Test listing webhooks."""
        response = self.client.list_webhooks()
        
        # Verify response structure
        self.assertIsInstance(response, dict)
        self.assertIn('data', response)
        self.assertIsInstance(response['data'], list)
    
    def test_create_get_update_delete_webhook(self):
        """Test full CRUD operations on a webhook."""
        self.require_write_access("webhook create/update/delete")
        # Create a webhook
        webhook_payload = {
            "data": {
                "target_url": "https://example.com/webhook-test",
                "subscriptions": [
                    {
                        "event_type": "record.created",
                        "filter": None
                    }
                ]
            }
        }
        
        create_response = self.client.create_webhook(payload=webhook_payload)
        self.assertIn('data', create_response)
        self.assertIn('id', create_response['data'])
        webhook_id = create_response['data']['id']['webhook_id']
        self.created_webhooks.append(webhook_id)
        
        # Get the webhook
        get_response = self.client.get_webhook(webhook_id)
        self.assertEqual(get_response['data']['id']['webhook_id'], webhook_id)
        self.assertEqual(get_response['data']['target_url'], "https://example.com/webhook-test")
        
        # Update the webhook
        update_payload = {
            "data": {
                "target_url": "https://example.com/webhook-updated"
            }
        }
        
        update_response = self.client.update_webhook(webhook_id, payload=update_payload)
        self.assertEqual(update_response['data']['target_url'], "https://example.com/webhook-updated")
        
        # Delete the webhook
        delete_response = self.client.delete_webhook(webhook_id)
        self.assertIsInstance(delete_response, dict)
        self.created_webhooks.remove(webhook_id)
