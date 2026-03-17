# TODO

## High Priority
1. Normalize write payload builders for workspace variability
- Add helper utilities for record/list/attribute payload generation based on discovered schema.
- Avoid hard-coded assumptions in integration tests and examples.

2. Add contract-check preflight utilities
- Add helper methods to inspect object/list attribute schemas before attempting create/update calls.
- Return actionable validation messages when a workspace contract doesn't match.

3. Improve CI strategy for integration tests
- Separate smoke tests from workspace-dependent tests.
- Add a dedicated profile/workspace for stricter, low-skip integration coverage.

## Medium Priority
1. Expand CLI coverage
- Add CLI entrypoints for common object/record/list mutation flows.
- Add `--help` style docs and examples for relationship scripts.

2. Documentation alignment
- Add a dedicated `docs/testing.md` for skip conditions, required scopes, and expected workspace setup.

## Low Priority
1. Add structured logging option to examples
- Optional verbose/debug output without editing script internals.

2. Add pagination examples to README
- Show idiomatic usage of `paginate_records` and cursor-based flows.
