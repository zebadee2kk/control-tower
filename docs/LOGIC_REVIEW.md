# Logic & Correctness Review

**Date:** 2026-02-25

## Workflow 1: Label Automation (`label-automation.yml`)

### Expected
- `state:done` label closes issue
- Closed issue gets `state:done` if missing
- `gate:needs-approval` label adds comment

### Actual
- ✅ Implements all three expected behaviors.
- ✅ No obvious infinite loop from `closed -> add state:done` because adding label does not reopen issue.
- ⚠️ Calls are not awaited; updates/comments may occasionally be dropped.

### Verdict
- **Functionally aligned** with requirement, but reliability improvements needed.

---

## Workflow 2: Nightly Decision Desk (`nightly-decision-desk.yml`)

### Expected
- Nightly schedule + manual dispatch
- Collect approval + blocked issues
- Create Decision Desk issue
- Close older Decision Desk issues

### Actual
- ✅ Schedule and manual dispatch present.
- ❌ Data handoff is broken (`steps.query.outputs` used incorrectly inside JS).
- ❌ Previous issue closure loop likely closes newest issue and keeps oldest (ordering bug).
- ⚠️ Creates Decision Desk issue **before** closing old ones, increasing race/confusion.
- ⚠️ Does not exclude the newly created Decision Desk issue from future source lists.

### Verdict
- **Not correct** in current form; high-priority fix required.

---

## Workflow 3: WIP Limit Check (`wip-limit-check.yml`)

### Expected
- Count build/research issues
- If either exceeds 3, block additional work item

### Actual
- ✅ Global counting logic exists.
- ❌ Can block/comment unrelated issues because it runs on broad issue events.
- ⚠️ `removeLabel` may target a label not present on triggering issue.
- ⚠️ No guard to ensure only the issue that caused overflow is modified.

### Verdict
- **Partially correct** but operationally unsafe until event scoping and target selection are fixed.

---

## Workflow 4: Weekly Cost Rollup (`weekly-cost-rollup.yml`)

### Expected
- Use issues updated in last 7 days
- Parse **budget comments** (`Budget: Xh, £Y`)
- Aggregate totals and report

### Actual
- ✅ Filters issues by `updated_at` and aggregates numeric totals.
- ❌ Parses `issue.body`, not comments.
- ⚠️ Only first 100 issues fetched; no pagination.
- ⚠️ Overrun threshold hardcoded (`cost > 100`) without documented policy source.

### Verdict
- **Requirement mismatch** for budget source (comments vs body); medium-priority fix.

## Overall Logic Status

- Ready for production: **No**
- Blocking defects: **Yes** (Nightly Decision Desk output handling and close-order logic)
