# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

py-attio is a lightweight Python wrapper for the Attio API. It provides a simple interface for interacting with Attio's CRM platform through their REST API v2.

## Development Commands

### Setup
```bash
# Install in development mode
pip install -e .

# Install dependencies
pip install requests
```

### Testing
```bash
# Run examples (no formal test suite currently)
python examples/objects/list_objects.py
python examples/records/crud_records.py
python examples/comprehensive_crud_demo.py

# Test relationship scripts (requires ATTIO_API_KEY)
python examples/relationships/associate_single_company_people_locations.py \
  --company google.com \
  --company-people-attr team \
  --company-locations-attr locations \
  --people-locations-attr associated_locations \
  --dry-run
```

### Building and Publishing
```bash
# Build package
python -m build

# Publishing is automated via GitHub Actions on release
# Manual publish (if needed):
twine upload dist/*
```

## Architecture

### Core Structure
- **py_attio/client.py**: Contains all API functionality
  - `BaseClient`: Internal class handling HTTP requests and authentication
  - `Client`: Public API providing methods for all Attio endpoints
- Single dependency on `requests` library
- All methods return JSON responses from the API

### API Method Pattern
Methods follow a consistent pattern:
```python
def method_name(self, required_param, optional_param=None, payload=None):
    """Docstring describing the endpoint"""
    endpoint = f"v2/endpoint/{required_param}"
    params = {}
    if optional_param:
        params['optional_param'] = optional_param
    return self._get(endpoint, params=params)  # or _post, _put, _delete
```

### Adding New Endpoints
1. Add method to `Client` class in `py_attio/client.py`
2. Follow existing naming conventions (snake_case matching API operations)
3. Include comprehensive docstring with parameter descriptions
4. Add example usage in `examples/` directory under appropriate subdirectory

### Working with Relationship Updates
When updating relationship attributes:
```python
# PATCH payload format for relationship attributes
payload = {
    "data": {
        "values": {
            "attribute_slug": [
                {"target_object": "target_obj_slug", "target_record_id": "uuid"}
            ]
        }
    }
}
client.update_record(object_id, record_id, payload)
```

### Error Handling
The client raises exceptions for HTTP errors with status code and response text. When implementing new features, maintain this pattern for consistency.

## Key Development Areas

### Current API Coverage
The client covers all major Attio API v2 endpoints including objects, records, lists, attributes, notes, tasks, threads, comments, webhooks, and workspace members.

### Recent Development Focus
- Adding missing parameters to existing methods (e.g., list_webhooks)
- Improving default payload handling for endpoints
- Bug fixes in method implementations (e.g., list_threads typo fix)
- Relationship attribute automation scripts for People <> Locations associations

## Relationship Attributes & Data Structures

### Understanding Attio Relationship Data
Relationship attributes in Attio store arrays of objects with these common patterns:
```python
# Record reference format (most common)
[{
    'target_object': 'people', 
    'target_record_id': 'uuid-here',
    'attribute_type': 'record-reference'
}]

# Alternative formats also supported
[{'record_id': 'uuid'}]
[{'id': {'record_id': 'uuid'}}]
[{'target': {'record_id': 'uuid'}}]
```

### Workspace-Specific Attribute Names
Attribute slugs vary by workspace configuration. Always inspect actual data structure:
- **Company->People**: Often `team`, `people`, `employees`, etc.
- **Company->Locations**: Often `locations`, `offices`, `sites`, etc. 
- **People->Locations**: Often `associated_locations`, `locations`, `offices`, etc.

### Debugging Relationship Issues
When relationship extraction fails:
1. Add debug output to see actual attribute names: `print(f"Keys: {list(values.keys())}")`
2. Inspect relationship data structure: `print(f"Attr: {values.get('attr_name')}")`
3. Test with actual workspace attribute slugs, not assumed names

### Example Scripts
- `examples/relationships/associate_people_locations.py`: Bulk association across all companies
- `examples/relationships/associate_single_company_people_locations.py`: Single company association by domain/URL

## Version Management
- Version is managed in `pyproject.toml`
- Follow semantic versioning
- Create GitHub releases to trigger automated PyPI publishing

