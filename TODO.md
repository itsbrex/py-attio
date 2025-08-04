# TODO: Fix Failing Tests

## Investigation Needed

### 1. Name Attribute Format Issue
- **Problem**: Records creation fails with "An invalid value was passed to attribute with slug 'name'"
- **Finding**: The API expects name values to include `attribute_type: 'personal-name'` field
- **Example working format**:
  ```python
  'name': [{
      'first_name': 'John',
      'last_name': 'Doe',
      'attribute_type': 'personal-name'
  }]
  ```
- **Action**: Update all record creation tests to include this field

### 2. List Creation Payload
- **Problem**: List creation returns "Body payload validation error"
- **Tried**: Adding `api_slug`, wrapping in `data`, using array for `parent_object`
- **Action**: Need to investigate exact required fields for list creation

### 3. Attribute Creation Payload  
- **Problem**: Custom attribute creation returns validation error
- **Action**: Investigate required fields and valid types for custom attributes

### 4. API Permission Scopes
- **Current limitations**:
  - No User Management scope - can't test workspace members
  - No Comments scope - can't test threads/comments
- **Action**: Document required scopes or make tests work with basic permissions

## Next Steps
1. Debug each failing endpoint with minimal payloads
2. Update test payloads based on findings
3. Consider adding example responses to documentation
4. Add retry logic for transient failures