# Testing Plan

**Date:** 2026-02-25

## Preconditions

- Test repository with all required labels created.
- Use non-production issues for validation.
- Enable `workflow_dispatch` runs for deterministic tests.

## 1) Label Automation

1. Create issue `A`.
2. Add `state:done` label.
   - Expected: issue closes.
3. Create issue `B`, close manually.
   - Expected: `state:done` label is added if missing.
4. Create issue `C`, add `gate:needs-approval`.
   - Expected: comment `Added to Decision Desk.` appears.
5. Regression: add/remove unrelated labels.
   - Expected: no side effects.

## 2) Nightly Decision Desk

1. Create 2 issues with `gate:needs-approval`.
2. Create 1 issue with `state:blocked`.
3. Trigger workflow manually.
4. Validate created issue title/body/labels.
5. Trigger again next day (or with date override in test branch).
   - Expected: only latest desk remains open.
6. Negative test: no qualifying issues.
   - Expected: issue still created with `None` sections (or documented skip behavior).

## 3) WIP Limit Check

1. Create 3 open issues with `state:build`.
2. Add `state:build` to a 4th issue.
   - Expected: 4th issue gets blocking comment, `state:blocked` added, `state:build` removed.
3. Close one build issue; retry label on blocked issue.
   - Expected: now permitted.
4. Add unrelated label to any issue.
   - Expected: no WIP comment/label churn.

## 4) Weekly Cost Rollup

1. Add budget entries in **issue comments** on multiple issues (`Budget: 5h, £80`).
2. Trigger workflow manually.
3. Validate totals and overrun section.
4. Include malformed budget text.
   - Expected: parser ignores malformed rows safely.

## Non-Functional Tests

- Run two dispatches concurrently for Nightly Decision Desk.
- Validate idempotency / no duplicate operational artifacts.
- Confirm failures include actionable logs.
