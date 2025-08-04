#!/usr/bin/env python3

"""
Custom Objects Example

This example demonstrates how to work with custom objects including:
- Listing only custom objects
- Getting object schema with attributes
- Creating, updating, and deleting custom objects
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
        # List only custom objects
        print("=== Custom Objects ===")
        custom_objects = client.list_custom_objects()
        print(f"Found {len(custom_objects.get('data', []))} custom objects")
        
        for obj in custom_objects.get('data', []):
            print(f"- {obj.get('api_slug')}: {obj.get('singular_noun')}")
        
        # Example: Get schema for a custom object
        if custom_objects.get('data'):
            first_object = custom_objects['data'][0]
            object_id = first_object.get('id', {}).get('object_id')
            
            if object_id:
                print(f"\n=== Schema for {first_object.get('singular_noun')} ===")
                schema = client.get_object_schema(object_id)
                
                if 'data' in schema and 'attributes' in schema['data']:
                    attributes = schema['data']['attributes'].get('data', [])
                    print(f"Attributes ({len(attributes)}):")
                    for attr in attributes:
                        attr_name = attr.get('api_slug', 'unknown')
                        attr_type = attr.get('type', 'unknown')
                        print(f"  - {attr_name} ({attr_type})")
        
        # Example: Create a new custom object
        print("\n=== Creating Custom Object ===")
        new_object_payload = {
            "api_slug": "sample_projects",
            "singular_noun": "Project",
            "plural_noun": "Projects",
            "description": "Custom project tracking object"
        }
        
        try:
            new_object = client.create_object(new_object_payload)
            print(f"Created object: {new_object.get('data', {}).get('singular_noun')}")
            
            # Get the new object ID for further operations
            new_object_id = new_object.get('data', {}).get('id', {}).get('object_id')
            
            if new_object_id:
                # Update the object
                update_payload = {
                    "description": "Updated project tracking object with more details"
                }
                updated_object = client.update_object(new_object_id, update_payload)
                print(f"Updated object description")
                
                # Clean up: Delete the test object
                client.delete_object(new_object_id)
                print(f"Deleted test object")
                
        except Exception as e:
            print(f"Note: Could not create test object (may already exist): {e}")
        
    except Exception as e:
        print(f"Error working with custom objects: {e}")

if __name__ == "__main__":
    main()