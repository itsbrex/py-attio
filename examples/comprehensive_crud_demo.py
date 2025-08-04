#!/usr/bin/env python3

"""
Comprehensive CRUD Demo

This example demonstrates the expanded CRUD capabilities of the Attio API wrapper,
showcasing operations across multiple resource types:
- Objects, Records, Lists, Attributes, Notes, Tasks, Comments, Threads, Webhooks
"""

import os
import sys

# Add the parent directory to sys.path to import py_attio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import py_attio

def demonstrate_enhanced_error_handling(client):
    """Demonstrate enhanced error handling"""
    print("\n=== Enhanced Error Handling Demo ===")
    
    try:
        # Try to get a non-existent object
        client.get_object("non_existent_object_id")
    except FileNotFoundError as e:
        print(f"✅ Caught 404 error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    try:
        # Try with invalid API key (simulate by using wrong object ID format)
        client.get_object("")
    except (ValueError, FileNotFoundError) as e:
        print(f"✅ Caught validation error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def demonstrate_custom_objects(client):
    """Demonstrate custom object operations"""
    print("\n=== Custom Objects Demo ===")
    
    try:
        # List all objects vs custom objects
        all_objects = client.list_objects()
        custom_objects = client.list_custom_objects()
        
        total_objects = len(all_objects.get('data', []))
        custom_count = len(custom_objects.get('data', []))
        system_count = total_objects - custom_count
        
        print(f"Total objects: {total_objects}")
        print(f"System objects: {system_count}")
        print(f"Custom objects: {custom_count}")
        
        # Show custom objects
        for obj in custom_objects.get('data', [])[:3]:  # Show first 3
            api_slug = obj.get('api_slug', 'unknown')
            name = obj.get('singular_noun', 'Unknown')
            print(f"  - {api_slug}: {name}")
            
    except Exception as e:
        print(f"Error demonstrating custom objects: {e}")

def demonstrate_comprehensive_crud(client):
    """Demonstrate CRUD operations across different resource types"""
    print("\n=== Comprehensive CRUD Operations Demo ===")
    
    try:
        # Get people object for record operations
        objects = client.list_objects()
        people_obj = None
        
        for obj in objects.get('data', []):
            if obj.get('api_slug') == 'people':
                people_obj = obj
                break
        
        if not people_obj:
            print("Could not find people object for demo")
            return
            
        object_id = people_obj.get('id', {}).get('object_id')
        print(f"Using object: {people_obj.get('singular_noun')} ({object_id})")
        
        # === RECORDS CRUD ===
        print("\n--- Records CRUD ---")
        
        # Create
        create_payload = {
            "data": {
                "values": {
                    "name": [{"first_name": "CRUD", "last_name": "Demo"}],
                    "email_addresses": [{"email_address": "crud.demo@example.com"}]
                }
            }
        }
        
        record = client.create_record(object_id, create_payload)
        record_id = record.get('data', {}).get('id', {}).get('record_id')
        print(f"✅ Created record: {record_id}")
        
        # Read
        record = client.get_record(object_id, record_id)
        print(f"✅ Read record: {record_id}")
        
        # Update
        update_payload = {
            "data": {
                "values": {
                    "name": [{"first_name": "Updated", "last_name": "Demo"}]
                }
            }
        }
        client.update_record(object_id, record_id, update_payload)
        print(f"✅ Updated record: {record_id}")
        
        # === NOTES CRUD ===
        print("\n--- Notes CRUD ---")
        
        # Create note
        note_payload = {
            "data": {
                "title": "Demo Note",
                "content": [{"type": "text", "text": "This is a demo note for CRUD testing"}],
                "parent_object": "people",
                "parent_record_id": record_id
            }
        }
        
        try:
            note = client.create_note(note_payload)
            note_id = note.get('data', {}).get('id', {}).get('note_id')
            print(f"✅ Created note: {note_id}")
            
            # Update note
            update_note_payload = {
                "data": {
                    "title": "Updated Demo Note",
                    "content": [{"type": "text", "text": "This note has been updated"}]
                }
            }
            client.update_note(note_id, update_note_payload)
            print(f"✅ Updated note: {note_id}")
            
            # Clean up note
            client.delete_note(note_id)
            print(f"✅ Deleted note: {note_id}")
            
        except Exception as e:
            print(f"Note operations not fully supported in demo: {e}")
        
        # === TASKS CRUD ===
        print("\n--- Tasks CRUD ---")
        
        task_payload = {
            "data": {
                "title": "Demo Task",
                "content": "This is a demo task for CRUD testing",
                "deadline_at": None,
                "parent_object": "people", 
                "parent_record_id": record_id
            }
        }
        
        try:
            task = client.create_task(task_payload)
            task_id = task.get('data', {}).get('id', {}).get('task_id')
            print(f"✅ Created task: {task_id}")
            
            # Update task with proper payload
            update_task_payload = {
                "data": {
                    "title": "Updated Demo Task",
                    "content": "This task has been updated"
                }
            }
            client.update_task(task_id, update_task_payload)
            print(f"✅ Updated task: {task_id}")
            
            # Clean up task
            client.delete_task(task_id)
            print(f"✅ Deleted task: {task_id}")
            
        except Exception as e:
            print(f"Task operations not fully supported in demo: {e}")
        
        # Clean up record
        client.delete_record(object_id, record_id)
        print(f"✅ Deleted record: {record_id}")
        
    except Exception as e:
        print(f"Error in comprehensive CRUD demo: {e}")

def demonstrate_pagination(client):
    """Demonstrate pagination capabilities"""
    print("\n=== Pagination Demo ===")
    
    try:
        # Get people object
        objects = client.list_objects()
        people_obj = None
        
        for obj in objects.get('data', []):
            if obj.get('api_slug') == 'people':
                people_obj = obj
                break
        
        if not people_obj:
            print("Could not find people object for pagination demo")
            return
            
        object_id = people_obj.get('id', {}).get('object_id')
        
        # Demo pagination with small page size
        print("Demonstrating automatic pagination (page_size=5)...")
        
        count = 0
        for record in client.paginate_records(object_id, page_size=5):
            count += 1
            if count <= 3:  # Show first 3
                values = record.get('values', {})
                name_data = values.get('name', [{}])[0] if values.get('name') else {}
                name = f"{name_data.get('first_name', '')} {name_data.get('last_name', '')}".strip()
                print(f"  Record {count}: {name or 'No name'}")
            elif count == 4:
                print("  ... (continuing pagination)")
                
            # Limit for demo
            if count >= 20:
                break
                
        print(f"✅ Paginated through {count} records automatically")
        
    except Exception as e:
        print(f"Error in pagination demo: {e}")

def main():
    # Initialize client with API token from environment
    api_token = os.getenv("ATTIO_API_KEY")
    if not api_token:
        print("Error: ATTIO_API_KEY environment variable not set")
        print("\nTo run this demo:")
        print("1. Get your API key from Attio settings")
        print("2. Set environment variable: export ATTIO_API_KEY=your_api_key")
        print("3. Run this script again")
        return
    
    client = py_attio.Client(api_token)
    
    print("🚀 Comprehensive CRUD Demo for py-attio")
    print("=====================================")
    
    try:
        # Test basic connectivity
        self_info = client.identify_self()
        workspace = self_info.get('data', {}).get('workspace', {})
        print(f"Connected to workspace: {workspace.get('name', 'Unknown')}")
        
        # Run demonstrations
        demonstrate_enhanced_error_handling(client)
        demonstrate_custom_objects(client)
        demonstrate_comprehensive_crud(client)
        demonstrate_pagination(client)
        
        print("\n✅ Demo completed successfully!")
        print("\nThe py-attio wrapper now supports:")
        print("- Complete CRUD operations for all resource types")
        print("- Enhanced error handling with specific exceptions")
        print("- Custom object management and schema inspection")
        print("- Automatic pagination and batch operations")
        print("- Improved developer experience")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\nPlease check:")
        print("- Your API key is valid")
        print("- You have necessary permissions")
        print("- Your workspace has the required objects")

if __name__ == "__main__":
    main()