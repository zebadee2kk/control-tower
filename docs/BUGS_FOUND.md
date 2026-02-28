# Bugs Found

## Critical
1. ~~`nightly-decision-desk` uses invalid cross-step output access (`steps.query.outputs`).~~ ✅ Fixed in Phase 2.5 (PR #21)
2. ~~Decision Desk cleanup logic can keep stale issue and close latest.~~ ✅ Fixed in Phase 2.5 (PR #21), enhanced in Bug #7 (PR #49)
3. Missing `await` on mutation calls across all workflows. ✅ Fixed in Phase 2.5 (PR #21)

## High
4. No pagination on repo issue queries.
5. WIP enforcement mutates unrelated triggering issue.
6. `removeLabel` may fail when label absent.

## Medium
7. Cost parser brittle and silently lossy.
8. Repeated gate comments without dedupe.
