# Bugs Found

## Bug #1: Nightly Decision Desk step output access is invalid

**File:** `.github/workflows/nightly-decision-desk.yml`  
**Line:** 38  
**Severity:** High

**Issue:**
The script uses `const { approvalIssues, blockedIssues } = steps.query.outputs;` inside `actions/github-script`. `steps` is not a JavaScript runtime object in this context, and no outputs are defined in the prior step.

**Impact:**
Decision Desk issue creation step fails at runtime; nightly automation is broken.

**Fix:**
Use `core.setOutput` in query step, then pass outputs via `${{ steps.query.outputs.approvalIssues }}` and parse JSON inside script.

**Test:**
Run `workflow_dispatch`; verify Decision Desk issue is created with populated approval/blocked sections.

---

## Bug #2: Nightly Decision Desk closes wrong issue due to ordering logic

**File:** `.github/workflows/nightly-decision-desk.yml`  
**Line:** 66-67  
**Severity:** High

**Issue:**
Loop closes `issues[0..n-2]` without explicit sort. Default ordering can cause newest issue to be closed while leaving oldest open.

**Impact:**
Operational desk continuity breaks; team may act on stale desk.

**Fix:**
Sort issues by created date descending and close all except the newest (or current run issue ID).

**Test:**
Seed two open desk issues; run workflow; verify newest remains open and older closes.

---

## Bug #3: WIP workflow can block unrelated issues

**File:** `.github/workflows/wip-limit-check.yml`  
**Line:** 6-13, 45-63  
**Severity:** Medium

**Issue:**
Workflow triggers on broad issue events and applies overflow actions to the triggering issue even when that issue did not add `state:build`/`state:research`.

**Impact:**
Incorrect comments/labels on unrelated issues; trust in automation degrades.

**Fix:**
Gate to `action == labeled` and label in (`state:build`, `state:research`), then only block if current issue is the one crossing threshold.

**Test:**
Add unrelated label to issue while WIP already exceeded; verify no blocking comment is posted.

---

## Bug #4: Weekly cost rollup parses issue body instead of comments

**File:** `.github/workflows/weekly-cost-rollup.yml`  
**Line:** 36-38  
**Severity:** Medium

**Issue:**
Workflow reads budget pattern from `issue.body`; requirements specify parsing budget **comments**.

**Impact:**
Rollup under-reports or reports incorrect totals.

**Fix:**
Fetch issue comments for updated issues and parse each comment body for budget entries.

**Test:**
Add `Budget: Xh, £Y` in comments only; run workflow; verify totals include those entries.
