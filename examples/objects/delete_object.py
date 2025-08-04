#!/usr/bin/env python3

"""
Delete Object Example

This example demonstrates how to delete a custom object using the Attio API wrapper.
Note: Only custom (user-defined) objects can be deleted, not system objects.
"""

import os
import sys

# Add the parent directory to sys.path to import py_attio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import py_attio

def main():
    # Initialize client with API token from environment
    api_token = os.getenv("ATTIO_API_KEY")
    if not api_token:
        print("Error: ATTIO_API_KEY environment variable not set")
        return
    
    client = py_attio.Client(api_token)
    
    try:
        # Example: Delete a custom object by ID
        object_id = "custom_object_id"  # Replace with actual object ID
        
        print(f"Deleting object: {object_id}")
        response = client.delete_object(object_id)
        
        print("Object deleted successfully!")
        print(f"Response: {response}")
        
    except FileNotFoundError as e:
        print(f"Object not found: {e}")
    except PermissionError as e:
        print(f"Permission denied: {e}")
    except Exception as e:
        print(f"Error deleting object: {e}")

if __name__ == "__main__":
    main()