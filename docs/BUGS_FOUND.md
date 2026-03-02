# Bugs Found

## Critical
1. ~~`nightly-decision-desk` uses invalid cross-step output access (`steps.query.outputs`).~~ ✅ Fixed in Phase 2.5 (PR #21)
2. ~~Decision Desk cleanup logic can keep stale issue and close latest.~~ ✅ Fixed in Phase 2.5 (PR #21), enhanced in Bug #7 (PR #49)
3. Missing `await` on mutation calls across all workflows. ✅ Fixed in Phase 2.5 (PR #21)

## High
4. No pagination on repo issue queries. *(Partially addressed: paginate() added to nightly-decision-desk, wip-limit-check, weekly-cost-rollup in PR #21)*
5. WIP enforcement mutates unrelated triggering issue. *(Partially mitigated: dispatch guard + label scope guard added in PR #21)*
6. ~~`removeLabel` may fail when label absent.~~ ✅ Fixed 2026-03-01 — re-fetch labels before removal guards race condition (hardening PR)

## Medium
7. Cost parser brittle and silently lossy.
8. Repeated gate comments without dedupe.

## Security / Operations (resolved)
- ~~GitHub Actions pinned to mutable version tags (`@v6`) instead of immutable commit SHAs.~~ ✅ Fixed 2026-03-01 — all workflows now pin `actions/github-script@d7906e4ad0b1822421a7e6a35d5ca353c962f410 # v6`
- ~~`contents: read` permission granted unnecessarily to all workflows.~~ ✅ Fixed 2026-03-01 — removed from all 4 workflows
- ~~`weekly-cost-rollup.yml` creates duplicate issues on rerun.~~ ✅ Fixed 2026-03-01 — ISO week-keyed idempotency guard added
