# Bugs Found and Resolved

**Last Updated:** 2026-03-02
**Total Bugs:** 8
**Fixed:** 5 (#1, #2, #3, #6, #7)
**Mitigated (open):** 2 (#4, #5 — guards added, full resolution deferred to Phase 3)
**Open:** 1 (#8 — P2, monitored)
**Phase 2 Target:** All P0/P1 bugs fixed ✅

> **Canonical source of truth.** For phase status and workflow details, see [PHASE_2_5_STATUS.md](PHASE_2_5_STATUS.md).

**Status Legend:**
- ✅ FIXED — Resolved, merged, verified in production
- ↗️ MITIGATED — Guards added, not fully resolved; deferred to Phase 3
- 📝 OPEN — Known issue, tracked, prioritized

---

## Critical (P1)

### Bug #1: Invalid Cross-Step Output Access

**Status:** ✅ FIXED
**Severity:** P1
**Fixed In:** PR #21
**Merged:** 2026-02-25
**Evidence:** [PR #21](https://github.com/zebadee2kk/control-tower/pull/21)
**Verified:** 2026-02-25 — Phase 2.5 validation (Issue #22)

**Description:**
`nightly-decision-desk` used `steps.query.outputs` to pass data between GitHub Actions steps — an invalid pattern that caused the workflow to silently fail when reading outputs.

**Resolution:**
Collapsed two `github-script` steps into a single script block, eliminating the cross-step output dependency entirely.

**Verification:**
Phase 2.5 validation (Issue #22): decision desk ran successfully in 3 manual `workflow_dispatch` triggers without any output access errors.

---

### Bug #2: Decision Desk Retention Ordering

**Status:** ✅ FIXED
**Severity:** P1
**Fixed In:** PR #21 (initial fix) + PR #49 (enhancement — see Bug #7)
**Merged:** 2026-02-25 (PR #21), 2026-02-28 (PR #49)
**Evidence:** [PR #21](https://github.com/zebadee2kk/control-tower/pull/21), [PR #49 commit](https://github.com/zebadee2kk/control-tower/commit/14520f3d1ebac1fa359c2ec991194e54c9556211)
**Verified:** 2026-03-01 — Issue #56 ran with correct retention behavior

**Description:**
Decision Desk cleanup logic could close the newest issue and keep a stale one. Missing sort order and absent title filter caused incorrect closure.

**Resolution:**
PR #21: Sort `state:awaiting-decision` issues by `created desc`; use `slice(1)` to keep the newest.
PR #49 (Bug #7): Added title filter `startsWith('Decision Desk')`; moved query before creation; added `state_reason: 'completed'`.

**Verification:**
Issue #56 (2026-03-01): Decision Desk correctly created new issue, closed previous with `state_reason: completed`.

---

### Bug #3: Missing `await` on Mutation Calls

**Status:** ✅ FIXED
**Severity:** P1
**Fixed In:** PR #21
**Merged:** 2026-02-25
**Evidence:** [PR #21](https://github.com/zebadee2kk/control-tower/pull/21)
**Verified:** 2026-02-25 — Phase 2.5 validation (Issue #22)

**Description:**
All 4 workflows were missing `await` on mutating GitHub API calls (`update`, `addLabels`, `createComment`, `create`, `removeLabel`). Mutations fired without waiting for completion, causing silent race conditions.

**Resolution:**
Added `await` to all 7 mutating API calls across all 4 workflows.

**Verification:**
Phase 2.5 validation (Issue #22): all API mutations confirmed synchronous in workflow execution logs.

---

## High (P2 — Mitigated)

### Bug #4: No Pagination on Repo Issue Queries

**Status:** ↗️ MITIGATED (open — deferred to Phase 3)
**Severity:** P2
**Impact:** Repos with >100 issues may have incomplete WIP counts or missing decision desk entries
**Mitigated In:** PR #21
**Next Steps:** Monitor in production; full cursor-based pagination in Phase 3 if issue count exceeds 100

**Description:**
`listForRepo` calls used a single-page result (no pagination). For repos with >100 issues, queries return incomplete data, causing incorrect WIP counts and potentially missing awaiting-decision issues.

**Mitigation:**
PR #21 replaced single-page `listForRepo` with `github.paginate()` in `nightly-decision-desk.yml`, `wip-limit-check.yml`, and `weekly-cost-rollup.yml`. Handles the common case; deep cursor-based edge cases remain.

---

### Bug #5: WIP Enforcement Mutates Unrelated Triggering Issue

**Status:** ↗️ MITIGATED (open — deferred to Phase 3)
**Severity:** P2
**Impact:** Rare — `workflow_dispatch` trigger or wrong-label issue could receive incorrect `state:blocked` label
**Mitigated In:** PR #21
**Next Steps:** Track occurrence frequency; tighten label scope in Phase 3

**Description:**
`wip-limit-check.yml` could mutate the triggering issue regardless of whether it needed the WIP state label. This risked adding `state:blocked` to issues unrelated to WIP tracking.

**Mitigation:**
PR #21 added two guards:
- `if (!context.payload.issue)` — dispatch safety: skip when there is no issue context
- `if (!currentLabels.includes(stateLabel))` — scope correctness: only add label if not already present

---

### Bug #6: `removeLabel` Race Condition

**Status:** ✅ FIXED
**Severity:** P1
**Fixed In:** PR #57
**Merged:** 2026-03-02
**Evidence:** [PR #57](https://github.com/zebadee2kk/control-tower/pull/57), [commit 86703fd](https://github.com/zebadee2kk/control-tower/commit/86703fdc809f28d643bacfdad9fa928401348fe3)
**Verified:** 2026-03-02 — PR #57 code review and merge

**Description:**
`wip-limit-check.yml` called `removeLabel` without verifying the label was still present. A concurrent event (e.g., user manually removing the label between the WIP check and the API call) would cause a GitHub API 422 error, failing the workflow run.

**Resolution:**
Added a re-fetch of the issue's current labels immediately before calling `removeLabel`. If the label is absent (removed concurrently), the call is skipped.

```javascript
// Re-fetch labels before removal to guard against concurrent label changes (Bug #6)
const freshIssue = await github.rest.issues.get({ owner, repo, issue_number });
const freshLabels = freshIssue.data.labels.map(l => l.name);
if (freshLabels.includes(stateLabel)) {
  await github.rest.issues.removeLabel({ owner, repo, issue_number, name: stateLabel });
}
```

**Verification:**
PR #57 testing: workflow executed without 422 errors; guard confirmed in code review.

---

## Medium (P0/P2)

### Bug #7: Decision Desk Template & Retention Logic

**Status:** ✅ FIXED
**Severity:** P0
**Fixed In:** PR #49
**Merged:** 2026-02-28
**Evidence:** [PR #49](https://github.com/zebadee2kk/control-tower/pull/49), [commit 14520f3](https://github.com/zebadee2kk/control-tower/commit/14520f3d1ebac1fa359c2ec991194e54c9556211)
**Verified:** 2026-03-01 — Issue #56 created with correct template; previous issue closed

**Description:**
Decision Desk issues lacked a structured decision template, making approval decisions inconsistent. The retention logic also lacked a title filter, risking closure of non-Decision-Desk issues.

**Resolution:**
- Added structured decision template with 4 options (✅ APPROVE / ⛔ REJECT / 🤔 DEFER / ❓ MORE INFO)
- Added title filter `startsWith('Decision Desk')` to retention logic
- Moved query logic before new issue creation (prevents the just-created issue from being immediately closed)
- Added `state_reason: 'completed'` for proper closure semantics
- Added debug logging for closed Decision Desks

**Verification:**
Issue #56 (2026-03-01): 3 manual `workflow_dispatch` runs — all scenarios passed. Template displayed correctly; old issue closed with `state_reason: completed`; no non-Decision-Desk issues affected.

---

### Bug #8: Repeated Gate Comments Without Dedupe

**Status:** 📝 OPEN
**Severity:** P2
**Impact:** Applying `gate:needs-approval` multiple times creates duplicate "Added to Decision Desk." comments on the issue
**Next Steps:** Phase 3 backlog — query existing comments before posting; skip if already present

**Description:**
`label-automation.yml` posts "Added to Decision Desk." every time the `gate:needs-approval` label is applied. If the label is removed and re-applied (or the event fires multiple times), duplicate comments accumulate.

**Workaround:**
None currently. Duplicate comments are cosmetic and do not affect workflow correctness.

---

## Security / Operations (Resolved)

Identified in the Perplexity security review (PR #53, 2026-02-28) and fixed in PR #57 (2026-03-02).

### SHA Pinning — Supply Chain Security

**Status:** ✅ FIXED
**Fixed In:** PR #57 (2026-03-02)
**Evidence:** [commit 86703fd](https://github.com/zebadee2kk/control-tower/commit/86703fdc809f28d643bacfdad9fa928401348fe3)

All 4 workflows used `actions/github-script@v6` (mutable tag) — vulnerable to supply-chain tag hijacking. Fixed by pinning to immutable commit SHA across all 4 workflows (7 steps total):

```yaml
uses: actions/github-script@d7906e4ad0b1822421a7e6a35d5ca353c962f410 # v6
```

---

### Permissions Minimization — Least Privilege

**Status:** ✅ FIXED
**Fixed In:** PR #57 (2026-03-02)
**Evidence:** [commit 86703fd](https://github.com/zebadee2kk/control-tower/commit/86703fdc809f28d643bacfdad9fa928401348fe3)

All workflows unnecessarily declared `contents: read` — unused, violating least privilege. Removed from all 4 workflows. Each now declares only `issues: write`.

---

### Weekly Rollup Idempotency

**Status:** ✅ FIXED
**Fixed In:** PR #57 (2026-03-02)
**Evidence:** [commit 86703fd](https://github.com/zebadee2kk/control-tower/commit/86703fdc809f28d643bacfdad9fa928401348fe3)

`weekly-cost-rollup.yml` created a new issue every run — manual reruns or scheduler retries produced duplicate issues. Fixed with ISO week-keyed idempotency: computes `YYYY-WXX` key, checks for an existing `cost:rollup` issue with that title, and exits early if one already exists. Issue #55 (2026-03-01) validated successfully.
