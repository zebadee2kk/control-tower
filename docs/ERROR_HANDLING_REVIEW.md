# Error Handling Review

**Date:** 2026-02-25

## Observations

- No workflow includes explicit `try/catch` in scripts.
- Most API calls are not `await`ed.
- No custom failure messages for known operational errors (missing labels, permission failures, 404/422 API responses).
- No idempotency guards to avoid duplicate comments/issues.

## Impact

- Hard-to-debug intermittent behavior.
- Partial operations can silently fail.
- Retries/re-runs may worsen state inconsistencies.

## Recommendations

1. Wrap script bodies in `try/catch` and use `core.setFailed(error.message)` with context.
2. `await` every GitHub REST mutation call.
3. Check for existing comments/labels before creating/removing.
4. Add guard clauses for event action and label names.
5. Emit structured logs (`core.info`) for key decisions.
