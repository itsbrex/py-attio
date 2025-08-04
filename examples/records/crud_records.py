#!/usr/bin/env python3

"""
Complete Record CRUD Example

This example demonstrates full CRUD operations for records:
- Create record
- Read record
- Update record  
- Delete record
- Pagination for large datasets
- Batch operations
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
        # Get the people object ID (standard Attio object)
        objects = client.list_objects()
        people_object = None
        
        for obj in objects.get('data', []):
            if obj.get('api_slug') == 'people':
                people_object = obj
                break
        
        if not people_object:
            print("Could not find people object")
            return
            
        object_id = people_object.get('id', {}).get('object_id')
        print(f"Working with object: {people_object.get('singular_noun')} ({object_id})")
        
        # === CREATE RECORD ===
        print("\n=== Creating Record ===")
        create_payload = {
            "data": {
                "values": {
                    "name": [{"first_name": "John", "last_name": "Doe"}],
                    "email_addresses": [{"email_address": "john.doe@example.com"}]
                }
            }
        }
        
        try:
            new_record = client.create_record(object_id, create_payload)
            record_id = new_record.get('data', {}).get('id', {}).get('record_id')
            print(f"Created record with ID: {record_id}")
            
            # === READ RECORD ===
            print("\n=== Reading Record ===")
            record = client.get_record(object_id, record_id)
            record_data = record.get('data', {})
            values = record_data.get('values', {})
            
            # Extract name and email
            name_data = values.get('name', [{}])[0] if values.get('name') else {}
            first_name = name_data.get('first_name', 'Unknown')
            last_name = name_data.get('last_name', '')
            
            email_data = values.get('email_addresses', [{}])[0] if values.get('email_addresses') else {}
            email = email_data.get('email_address', 'No email')
            
            print(f"Record: {first_name} {last_name} ({email})")
            
            # === UPDATE RECORD ===
            print("\n=== Updating Record ===")
            update_payload = {
                "data": {
                    "values": {
                        "name": [{"first_name": "Jane", "last_name": "Smith"}],
                        "email_addresses": [{"email_address": "jane.smith@example.com"}]
                    }
                }
            }
            
            updated_record = client.update_record(object_id, record_id, update_payload)
            print("Record updated successfully")
            
            # Verify update
            updated_record = client.get_record(object_id, record_id)
            updated_values = updated_record.get('data', {}).get('values', {})
            updated_name = updated_values.get('name', [{}])[0] if updated_values.get('name') else {}
            updated_first = updated_name.get('first_name', 'Unknown')
            updated_last = updated_name.get('last_name', '')
            print(f"Updated record: {updated_first} {updated_last}")
            
            # === DELETE RECORD ===
            print("\n=== Deleting Record ===")
            client.delete_record(object_id, record_id)
            print("Record deleted successfully")
            
            # Verify deletion
            try:
                client.get_record(object_id, record_id)
                print("Warning: Record still exists after deletion")
            except FileNotFoundError:
                print("Confirmed: Record has been deleted")
                
        except Exception as e:
            print(f"Error in CRUD operations: {e}")
        
        # === PAGINATION EXAMPLE ===
        print("\n=== Pagination Example ===")
        try:
            record_count = 0
            print("Iterating through all records using pagination...")
            
            # Use pagination generator to iterate through all records
            for record in client.paginate_records(object_id, page_size=50):
                record_count += 1
                if record_count <= 5:  # Show first 5 records
                    values = record.get('values', {})
                    name_data = values.get('name', [{}])[0] if values.get('name') else {}
                    name = f"{name_data.get('first_name', '')} {name_data.get('last_name', '')}".strip()
                    print(f"  Record {record_count}: {name or 'No name'}")
                elif record_count == 6:
                    print("  ... (showing first 5 records)")
                    
                # Limit output for demo
                if record_count >= 100:
                    break
                    
            print(f"Total records processed: {record_count}")
            
        except Exception as e:
            print(f"Error in pagination: {e}")
        
        # === BATCH OPERATIONS EXAMPLE ===
        print("\n=== Batch Operations Example ===")
        try:
            # Create multiple test records in batch
            test_records = []
            for i in range(3):
                test_records.append({
                    "data": {
                        "values": {
                            "name": [{"first_name": f"Test{i}", "last_name": "User"}],
                            "email_addresses": [{"email_address": f"test{i}@example.com"}]
                        }
                    }
                })
            
            print(f"Creating {len(test_records)} records in batch...")
            results = client.batch_create_records(object_id, test_records, batch_size=2)
            
            successful_creates = [r for r in results if 'error' not in r]
            failed_creates = [r for r in results if 'error' in r]
            
            print(f"Successfully created: {len(successful_creates)} records")
            if failed_creates:
                print(f"Failed to create: {len(failed_creates)} records")
            
            # Clean up test records
            for result in successful_creates:
                try:
                    record_id = result.get('data', {}).get('id', {}).get('record_id')
                    if record_id:
                        client.delete_record(object_id, record_id)
                except:
                    pass  # Ignore cleanup errors
                    
            print("Cleaned up test records")
            
        except Exception as e:
            print(f"Error in batch operations: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()