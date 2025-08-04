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
python examples/objects/get_all_objects.py
python examples/records/get_all_people.py
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

### Error Handling
The client raises exceptions for HTTP errors with status code and response text. When implementing new features, maintain this pattern for consistency.

## Key Development Areas

### Current API Coverage
The client covers all major Attio API v2 endpoints including objects, records, lists, attributes, notes, tasks, threads, comments, webhooks, and workspace members.

### Recent Development Focus
- Adding missing parameters to existing methods (e.g., list_webhooks)
- Improving default payload handling for endpoints
- Bug fixes in method implementations (e.g., list_threads typo fix)

## Version Management
- Version is managed in `pyproject.toml`
- Follow semantic versioning
- Create GitHub releases to trigger automated PyPI publishing