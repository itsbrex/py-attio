# Testing Guide

## Quick Start

```bash
uv sync --group dev
uv run test -q
```

## Environment
Tests require an Attio API key:

```env
ATTIO_API_KEY=your_api_key_here
```

The suite is integration-oriented and runs against a live workspace.

## Expected Outcomes
A passing run may include skips. Skips are normal when:
- API token lacks required scopes (for example, Comments, User Management)
- Workspace schema does not match test create payload assumptions
- No suitable records exist to construct thread query context

## Current Baseline
Latest verified baseline:
- 11 passed
- 10 skipped
- 0 failed

## Scope Guidance
- `tests/test_webhooks.py`: good indicator of write-flow health.
- `tests/test_threads_comments.py`: requires comments scope and valid record context.
- `tests/test_workspace_members.py`: requires user-management scope.

## Troubleshooting
1. If many create tests skip/fail with 400 validation errors:
- Confirm workspace schema for `people`, list definitions, and custom attributes.
- Use object/list attribute discovery before assuming payload shape.

2. If auth errors occur:
- Verify `ATTIO_API_KEY` is set in shell or `.env`.
- Verify token scopes in Attio.
