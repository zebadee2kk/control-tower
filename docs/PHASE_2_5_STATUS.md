# Phase 2.5 Status — Control Tower Automation

**Updated:** 2026-02-25
**Branch:** `phase-2.5-bug-fixes` → merged to `main`

---

## What Was Done

Phase 2.5 fixed 6 critical bugs identified in the Codex deep review (Issue #18). All fixes live in PR #21 and have been validated by Claude Code (Issue #22 test plan).

### Bugs Fixed (5/6)

| Bug | Workflow | Fix |
|-----|----------|-----|
| Cross-step output | `nightly-decision-desk.yml` | Collapsed two `github-script` steps into one script block — eliminates `steps.query.outputs` anti-pattern |
| Retention ordering | `nightly-decision-desk.yml` | Sort `state:awaiting-decision` issues by `created desc` + `slice(1)` keeps newest and closes all older |
| Missing `await` | All 4 workflows | Added `await` to all 7 mutating API calls (update, addLabels, createComment, create, removeLabel) |
| No pagination | `nightly-decision-desk.yml`, `wip-limit-check.yml`, `weekly-cost-rollup.yml` | Replaced single-page `listForRepo` with `github.paginate()` |
| WIP scope | `wip-limit-check.yml` | Added two guards: `if (!context.payload.issue)` (dispatch safety) + `if (!currentLabels.includes(stateLabel))` (scope correctness) |

### Known Remaining Bug (Bug #6)

**Concurrency control not implemented.** No `concurrency:` key was added.

**Impact:** Running `nightly-decision-desk` or `weekly-cost-rollup` twice simultaneously:
- Creates duplicate report issues
- Causes concurrent close attempts → `422 Validation Failed` on one run

**Fix (2 lines per affected workflow):**
```yaml
concurrency:
  group: ${{ github.workflow }}
  cancel-in-progress: false
```

**Affected:** `nightly-decision-desk.yml`, `weekly-cost-rollup.yml`
**Workaround:** Only one trigger source in production (cron schedule), so real-world concurrency risk is low but not zero.

---

## Current Workflow State

| Workflow | Trigger | Status | Notes |
|----------|---------|--------|-------|
| `label-automation.yml` | `issues: labeled/closed` | Production-ready ✅ | All 3 automated behaviors working |
| `nightly-decision-desk.yml` | `schedule: 9PM UTC` + `workflow_dispatch` | Usable with caveat ⚠️ | Works correctly; missing concurrency key |
| `wip-limit-check.yml` | `issues: labeled/opened/reopened` | Production-ready ✅ | WIP=3 enforced correctly |
| `weekly-cost-rollup.yml` | `schedule: Sunday 6PM UTC` + `workflow_dispatch` | Usable with caution ⚠️ | No idempotency; no concurrency key |

---

## Pre-existing Limitations (Not in Scope of Phase 2.5)

1. **Cost rollup idempotency** — workflow creates a new rollup issue every trigger, no weekly deduplication
2. **Cost data source** — parses `issue.body` for `Budget: Xh, £Y` pattern; no comment-based tracking
3. **Gate comment deduplication** — adding `gate:needs-approval` multiple times creates multiple "Added to Decision Desk." comments
4. **Decision Desk eventual consistency** — in rapid-fire testing, ~90s GitHub API label-index lag means a just-created DD issue may survive one extra run cycle; no impact on nightly production schedule

---

## Next Steps

### Immediate (to fully close Issue #18)
- [ ] Add `concurrency:` key to `nightly-decision-desk.yml` and `weekly-cost-rollup.yml`
- [ ] Re-run test 2.4 (concurrent triggers) to confirm fix

### Follow-up
- [ ] Implement cost rollup idempotency (check for existing rollup for current week before creating)
- [ ] Decide on comment-based vs body-based cost tracking
- [ ] Gate comment deduplication (check for existing comment before posting)

---

## Related Issues / PRs

| Ref | Title | Status |
|-----|-------|--------|
| Issue #18 | [Phase 2.5] Critical Workflow Bug Fixes | Open — partially resolved by PR #21 |
| PR #21 | Fix 6 critical workflow bugs | Merged to main |
| Issue #22 | [Testing] Validate Phase 2.5 Bug Fixes | Results documented — 5/6 bugs confirmed fixed |
| Issue #13 | Phase 2 Automation Pilot | In planning |
