# Test Results Summary

## Current Status
Latest verified run:

```bash
uv run test -q
```

Result:
- 11 passed
- 10 skipped
- 0 failed

## Why Tests Are Skipped
The suite is integration-heavy and runs against a live Attio workspace. Skips are expected in these cases:
- Missing API scopes (for example, comments or user management)
- Workspace/API contract mismatch for create payloads (schema-specific validation)
- No suitable records available for thread-context tests

## Practical Interpretation
- Core read/list flows and webhook flows are passing.
- Workspace-dependent create flows are guarded to skip instead of failing hard when the target workspace contract differs.

## Runbook

```bash
# Sync local dev/test dependencies
uv sync --group dev

# Run the test suite
uv run test -q

# Verbose output
uv run test -v
```

## Environment
Create a `.env` file:

```env
ATTIO_API_KEY=your_api_key_here
```

## Notes
- Test behavior is intentionally defensive for cross-workspace compatibility.
- For stricter CI, run against a dedicated Attio workspace with known schema/scopes and reduce skip conditions.
