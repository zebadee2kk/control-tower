# Bugs Found

## Critical
1. `nightly-decision-desk` uses invalid cross-step output access (`steps.query.outputs`).
2. Decision Desk cleanup logic can keep stale issue and close latest.
3. Missing `await` on mutation calls across all workflows.

## High
4. No pagination on repo issue queries.
5. WIP enforcement mutates unrelated triggering issue.
6. `removeLabel` may fail when label absent.

## Medium
7. Cost parser brittle and silently lossy.
8. Repeated gate comments without dedupe.
