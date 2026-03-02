# Handoff: Security Hardening + Bug #6 + Rollup Idempotency

**Date:** 2026-03-01
**Completed by:** Claude Code (claude-sonnet-4-6)
**Handoff to:** Perplexity
**Branch:** `main` (PR to be merged)

---

## What Was Completed

This session addressed all P0/P1 items from the Perplexity security review (2026-02-28).

### 1. Action SHA Pinning (P0 — Security)

**Problem:** All 4 workflows used `actions/github-script@v6` (mutable tag) — vulnerable to supply-chain tag hijacking.

**Fix:** Pinned to immutable commit SHA in all 4 workflows:
```yaml
uses: actions/github-script@d7906e4ad0b1822421a7e6a35d5ca353c962f410 # v6
```

**Files changed:**
- `.github/workflows/nightly-decision-desk.yml`
- `.github/workflows/wip-limit-check.yml`
- `.github/workflows/weekly-cost-rollup.yml`
- `.github/workflows/label-automation.yml` (3 steps pinned)

---

### 2. Permissions Minimization (P0 — Security)

**Problem:** All workflows declared `contents: read` which was unused — violates least-privilege.

**Fix:** Removed `contents: read` from all 4 workflows. Each now has only:
```yaml
permissions:
  issues: write
```

**Files changed:** Same 4 files above.

---

### 3. Bug #6 Fixed — removeLabel Race Condition (P1 — Reliability)

**Problem:** `wip-limit-check.yml` called `removeLabel` without re-checking whether the label was still present. A concurrent event (e.g. user manually removing the label) would cause a GitHub API 422 error.

**Fix:** Added a re-fetch of the issue's labels immediately before calling `removeLabel`, and skip the call if the label is no longer present.

```javascript
// Re-fetch labels before removal to guard against concurrent label changes (Bug #6)
const freshIssue = await github.rest.issues.get({ ... });
const freshLabels = freshIssue.data.labels.map(l => l.name);
if (freshLabels.includes(stateLabel)) {
  await github.rest.issues.removeLabel({ ... });
}
```

**File changed:** `.github/workflows/wip-limit-check.yml`

---

### 4. Weekly Rollup Idempotency (P1 — Reliability)

**Problem:** `weekly-cost-rollup.yml` created a new issue every time it ran — manual reruns or scheduler retries produced duplicate issues.

**Fix:** Computes an ISO week key (`YYYY-WXX`), queries for an existing `cost:rollup` issue with that exact title, and exits early if one already exists.

```javascript
const weekKey = `${year}-W${String(weekNum).padStart(2, '0')}`;
const rollupTitle = `Weekly Cost Rollup (${weekKey})`;
// ... check for existing, skip if found
```

Title format also changed from `YYYY-MM-DD` (date) to `YYYY-WXX` (ISO week) to be semantically correct.

**File changed:** `.github/workflows/weekly-cost-rollup.yml`

---

### 5. Documentation Updated (P1 — Documentation integrity)

**Updated:**
- `docs/BUGS_FOUND.md` — Bug #6 marked fixed with evidence; security items added as resolved; Bug #4/#5 status clarified
- `docs/PHASE_2_5_STATUS.md` — Hardening section added, workflow status table updated, Next Steps reconciled

---

## Current State After This PR

### Workflow Security & Reliability

| Workflow | SHA Pinned | Permissions | Bug #6 | Idempotent |
|----------|-----------|-------------|--------|------------|
| `nightly-decision-desk.yml` | ✅ | `issues: write` only | N/A | ✅ (dedupes by title) |
| `wip-limit-check.yml` | ✅ | `issues: write` only | ✅ Fixed | N/A |
| `weekly-cost-rollup.yml` | ✅ | `issues: write` only | N/A | ✅ ISO week key |
| `label-automation.yml` | ✅ (3 steps) | `issues: write` only | N/A | N/A |

### Open Bugs (from BUGS_FOUND.md)

| Bug | Priority | Status |
|-----|----------|--------|
| Bug #4: No pagination | High | Partially mitigated (paginate() added) |
| Bug #5: WIP scope | High | Partially mitigated (guards added) |
| Bug #8: Gate comment dedupe | Medium | Open |

---

## Remaining Work

### Recommended Next Steps

1. **Bug #8** (Medium): Gate comment deduplication — `label-automation.yml` posts "Added to Decision Desk." every time `gate:needs-approval` is applied. Fix: query for existing comment before posting.

2. **Phase 3A — ai-cost-tracker deployment**: Deploy ai-cost-tracker locally via Docker Compose (see `docs/AI_COST_TRACKER_QUICKSTART.md`), then build the control-tower integration layer.

3. **Phase 3A — Integration layer**: Build `src/integrations/cost_tracker.py` to call ai-cost-tracker REST API from the Decision Desk workflow.

### Suggested Prompt for Next Session

> Review `docs/BUGS_FOUND.md` and `docs/PHASE_2_5_STATUS.md` for open items. Implement Bug #8 (gate comment deduplication in `label-automation.yml`): before posting "Added to Decision Desk.", query the issue's existing comments for a match and skip if already present. Then create a PR, update BUGS_FOUND.md to mark Bug #8 resolved, and update PHASE_2_5_STATUS.md. After that, refer to `docs/AI_COST_TRACKER_QUICKSTART.md` and `docs/HANDOFF_2026-03-01_AI_COST_TRACKER_DEPLOYMENT.md` for Phase 3A integration work.

---

## Files Modified This Session

### Changed:
- `.github/workflows/nightly-decision-desk.yml` — SHA pin, removed `contents: read`
- `.github/workflows/wip-limit-check.yml` — SHA pin, removed `contents: read`, Bug #6 fix
- `.github/workflows/weekly-cost-rollup.yml` — SHA pin, removed `contents: read`, idempotency
- `.github/workflows/label-automation.yml` — SHA pin (3 steps), removed `contents: read`
- `docs/BUGS_FOUND.md` — Bug #6 marked fixed, security items resolved, Bug #4/#5 clarified
- `docs/PHASE_2_5_STATUS.md` — Hardening section added, table updated, checklist updated

### New:
- `docs/HANDOFF_2026-03-01_HARDENING.md` — This file

---

**Handoff Complete** — All P0/P1 items from Perplexity review addressed.
