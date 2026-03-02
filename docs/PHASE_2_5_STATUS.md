# Phase 2.5 Status — Control Tower Automation

> **Bug details and verification evidence:** see [BUGS_FOUND.md](BUGS_FOUND.md) (canonical source of truth).

**Last Updated:** 2026-03-02
**Phase Status:** COMPLETE ✅
**Security Hardening:** COMPLETE ✅ (PR #57, 2026-03-02)
**Documentation:** COMPLETE ✅ (2026-03-02)

---

## Bug Status Summary

See [BUGS_FOUND.md](BUGS_FOUND.md) for complete details, PR links, and verification evidence.

| Bug | Title | Status |
|-----|-------|--------|
| #1 | Invalid cross-step output access | ✅ Fixed — PR #21 (2026-02-25) |
| #2 | Decision Desk retention ordering | ✅ Fixed — PR #21 + PR #49 (2026-02-25/28) |
| #3 | Missing `await` on mutation calls | ✅ Fixed — PR #21 (2026-02-25) |
| #4 | No pagination on issue queries | ↗️ Mitigated — `paginate()` added (PR #21); open P2 |
| #5 | WIP enforcement scope | ↗️ Mitigated — guards added (PR #21); open P2 |
| #6 | `removeLabel` race condition | ✅ Fixed — PR #57 (2026-03-02) |
| #7 | Decision Desk template & retention | ✅ Fixed — PR #49 (2026-02-28) |
| #8 | Gate comment dedupe | 📝 Open — P2, Phase 3 backlog |

**Phase 2 Goal Achieved:** All P0/P1 bugs resolved ✅

---

## Security Hardening (PR #57)

**Completed:** 2026-03-02
**PR:** [#57](https://github.com/zebadee2kk/control-tower/pull/57)
**Commit:** [86703fd](https://github.com/zebadee2kk/control-tower/commit/86703fdc809f28d643bacfdad9fa928401348fe3)

**P0 — Supply Chain Security:**
- ✅ All 4 workflows pinned to immutable SHA `d7906e4ad0b1822421a7e6a35d5ca353c962f410 # v6`
- ✅ Removed unused `contents: read` from all 4 workflows — least privilege enforced

**P1 — Reliability:**
- ✅ Bug #6 fixed: `wip-limit-check.yml` re-fetches labels before `removeLabel` (race condition guard)
- ✅ `weekly-cost-rollup.yml`: ISO week-keyed idempotency prevents duplicate issues on reruns

---

## Bug #7 Fixed (PR #49)

**Completed:** 2026-02-28
**PR:** [#49](https://github.com/zebadee2kk/control-tower/pull/49)

**Decision Desk Template & Enhanced Retention Logic**

- ✅ Added decision template with 4 options (APPROVE/REJECT/DEFER/MORE INFO)
- ✅ Enhanced retention logic: title filter prevents closing non-Decision-Desk issues
- ✅ Query moved before creation: prevents new issue from being immediately closed
- ✅ Added `state_reason: 'completed'` and debug logging
- ✅ Tested with 3 manual workflow runs — all scenarios passed

---

## What Was Done in Phase 2.5

Phase 2.5 fixed 6 critical bugs identified in the Codex deep review (Issue #18). All fixes are in PR #21 and validated in Issue #22.

### Bugs Fixed (PR #21 — 2026-02-25)

| Bug | Workflow | Fix |
|-----|----------|-----|
| Cross-step output | `nightly-decision-desk.yml` | Collapsed two `github-script` steps into one — eliminates `steps.query.outputs` anti-pattern |
| Retention ordering | `nightly-decision-desk.yml` | Sort `state:awaiting-decision` issues by `created desc` + `slice(1)` keeps newest, closes older |
| Missing `await` | All 4 workflows | Added `await` to all 7 mutating API calls |
| No pagination | `nightly-decision-desk.yml`, `wip-limit-check.yml`, `weekly-cost-rollup.yml` | Replaced `listForRepo` with `github.paginate()` |
| WIP scope | `wip-limit-check.yml` | Added two guards: dispatch safety + label scope correctness |
| Concurrency control | `nightly-decision-desk.yml`, `weekly-cost-rollup.yml` | Added `concurrency` block (PR #40) |

---

## Workflow Status

| Workflow | Status | SHA Pinned | Last Updated | Notes |
|----------|--------|------------|--------------|-------|
| `nightly-decision-desk.yml` | ✅ Production | ✅ PR #57 | 2026-03-02 | Bug #7 fixed, template working; Issue #56 validated |
| `wip-limit-check.yml` | ✅ Production | ✅ PR #57 | 2026-03-02 | Bug #6 fixed, race condition resolved |
| `weekly-cost-rollup.yml` | ✅ Production | ✅ PR #57 | 2026-03-02 | ISO week idempotency; Issue #55 validated |
| `label-automation.yml` | ✅ Production | ✅ PR #57 | 2026-03-02 | SHA pinned; Bug #8 (comments) open P2 |

---

## Known Limitations (Out of Scope for Phase 2)

1. **Cost data source** — parses `issue.body` for `Budget: Xh, £Y` pattern; no comment-based tracking
2. **Decision Desk eventual consistency** — in rapid-fire testing, ~90s GitHub API label-index lag means a just-created issue may survive one extra run cycle; no impact on nightly schedule
3. **Bug #4 (partial)** — pagination covers common case; deep cursor-based pagination deferred to Phase 3
4. **Bug #5 (partial)** — WIP scope guards cover common case; full label scoping deferred to Phase 3

---

## Next Steps (Phase 3A)

- [ ] **Bug #8** — Gate comment deduplication: query existing comments before posting in `label-automation.yml`
- [ ] Deploy ai-cost-tracker locally (see [AI_COST_TRACKER_QUICKSTART.md](AI_COST_TRACKER_QUICKSTART.md))
- [ ] Build `src/integrations/cost_tracker.py` integration layer

---

## Related Issues / PRs

| Ref | Title | Status |
|-----|-------|--------|
| Issue #18 | [Phase 2.5] Critical Workflow Bug Fixes | Open — resolved by PR #21 + #49 + #57 |
| PR #21 | Fix 6 critical workflow bugs (Phase 2.5) | ✅ Merged 2026-02-25 |
| PR #40 | Add concurrency control to scheduled workflows | ✅ Merged 2026-02-25 |
| PR #41 | Update Phase 2.5 handover docs | ✅ Merged 2026-02-25 |
| Issue #22 | [Testing] Validate Phase 2.5 Bug Fixes | Results documented — 5/6 bugs confirmed fixed |
| PR #49 | Fix Bug #7 — Decision Desk template & retention | ✅ Merged 2026-02-28 |
| PR #53 | Codex security and documentation review | ✅ Merged 2026-02-28 |
| PR #57 | Security hardening — SHA pin, Bug #6, rollup idempotency | ✅ Merged 2026-03-02 |
