# Phase 2.5 Status — Control Tower Automation

**Updated:** 2026-03-01
**Branch:** `phase-2.5-bug-fixes` → merged to `main`

---

## Recent Updates

### Security Hardening + Bug #6 + Rollup Idempotency (2026-03-01) — Hardening PR

**Action SHA pinning (P0)**
- ✅ All 4 workflows now pin `actions/github-script` to immutable commit SHA `d7906e4ad0b1822421a7e6a35d5ca353c962f410 # v6`
- ✅ `contents: read` permission removed from all 4 workflows (was unused; principle of least privilege)

**Bug #6 Fixed — `removeLabel` race condition (P1)**
- ✅ `wip-limit-check.yml`: re-fetches issue labels immediately before calling `removeLabel`; skips removal if label is already absent, preventing 422 errors from concurrent label changes

**Weekly rollup idempotency (P1)**
- ✅ `weekly-cost-rollup.yml`: computes ISO week key (e.g. `2026-W09`), queries for existing rollup with that title, and exits early if one already exists — prevents duplicates on manual reruns or scheduler retries
- ✅ Rollup issue title format changed from `YYYY-MM-DD` to `YYYY-WXX` to match ISO week

**Workflow status after this PR:**

| Workflow | Status |
|----------|--------|
| `label-automation.yml` | Production-ready ✅ |
| `nightly-decision-desk.yml` | Production-ready ✅ |
| `wip-limit-check.yml` | Production-ready ✅ |
| `weekly-cost-rollup.yml` | Production-ready ✅ (idempotency added) |

---

### Bug #7 Fixed (2026-02-28) — PR #49

**Decision Desk Template & Enhanced Retention Logic**

- ✅ Added decision template with 4 options (APPROVE/REJECT/DEFER/MORE INFO)
- ✅ Enhanced retention logic to filter by title pattern (`startsWith('Decision Desk')`)
- ✅ Added debug logging for closed Decision Desks
- ✅ Tested with 3 manual workflow runs - all scenarios passed

**Result:** Decision Desk workflow now provides clear decision guidance and more robust retention logic.

---

## What Was Done

Phase 2.5 fixed 6 critical bugs identified in the Codex deep review (Issue #18). All fixes live in PR #21 and have been validated by Claude Code (Issue #22 test plan).

### Bugs Fixed (6/6)

| Bug | Workflow | Fix |
|-----|----------|-----|
| Cross-step output | `nightly-decision-desk.yml` | Collapsed two `github-script` steps into one script block — eliminates `steps.query.outputs` anti-pattern |
| Retention ordering | `nightly-decision-desk.yml` | Sort `state:awaiting-decision` issues by `created desc` + `slice(1)` keeps newest and closes all older |
| Missing `await` | All 4 workflows | Added `await` to all 7 mutating API calls (update, addLabels, createComment, create, removeLabel) |
| No pagination | `nightly-decision-desk.yml`, `wip-limit-check.yml`, `weekly-cost-rollup.yml` | Replaced single-page `listForRepo` with `github.paginate()` |
| WIP scope | `wip-limit-check.yml` | Added two guards: `if (!context.payload.issue)` (dispatch safety) + `if (!currentLabels.includes(stateLabel))` (scope correctness) |
| Concurrency control | `nightly-decision-desk.yml`, `weekly-cost-rollup.yml` | Added `concurrency` block with `group: ${{ github.workflow }}` and `cancel-in-progress: false` (PR #40) |

### Concurrency Status (Bug #6)

**Fixed:** `concurrency` added to `nightly-decision-desk.yml` and `weekly-cost-rollup.yml` in PR #40.

**Test:** Two manual `workflow_dispatch` triggers per workflow on `main` succeeded without duplicate creation errors.

---

## Current Workflow State

| Workflow | Trigger | Status | Notes |
|----------|---------|--------|-------|
| `label-automation.yml` | `issues: labeled/closed` | Production-ready ✅ | All 3 automated behaviors working |
| `nightly-decision-desk.yml` | `schedule: 9PM UTC` + `workflow_dispatch` | Production-ready ✅ | Concurrency guard, SHA-pinned |
| `wip-limit-check.yml` | `issues: labeled/opened/reopened` | Production-ready ✅ | WIP=3 enforced, removeLabel race fixed |
| `weekly-cost-rollup.yml` | `schedule: Sunday 6PM UTC` + `workflow_dispatch` | Production-ready ✅ | ISO week idempotency added |

---

## Pre-existing Limitations (Not in Scope of Phase 2.5)

1. **Cost rollup idempotency** — workflow creates a new rollup issue every trigger, no weekly deduplication
2. **Cost data source** — parses `issue.body` for `Budget: Xh, £Y` pattern; no comment-based tracking
3. **Gate comment deduplication** — adding `gate:needs-approval` multiple times creates multiple "Added to Decision Desk." comments
4. **Decision Desk eventual consistency** — in rapid-fire testing, ~90s GitHub API label-index lag means a just-created DD issue may survive one extra run cycle; no impact on nightly production schedule

---

## Next Steps

### Follow-up
- [x] ~~Implement cost rollup idempotency~~ — Done 2026-03-01 (ISO week key)
- [ ] Decide on comment-based vs body-based cost tracking
- [ ] Gate comment deduplication (Bug #8 — check for existing comment before posting)

---

## Related Issues / PRs

| Ref | Title | Status |
|-----|-------|--------|
| Issue #18 | [Phase 2.5] Critical Workflow Bug Fixes | Open — partially resolved by PR #21 |
| PR #21 | Fix 6 critical workflow bugs | Merged to main |
| PR #40 | Add concurrency control to scheduled workflows | Merged to main |
| Issue #22 | [Testing] Validate Phase 2.5 Bug Fixes | Results documented — 5/6 bugs confirmed fixed |
| Issue #13 | Phase 2 Automation Pilot | In planning |
