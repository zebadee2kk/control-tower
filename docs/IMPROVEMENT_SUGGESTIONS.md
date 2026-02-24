# Improvement Suggestions

**Date:** 2026-02-25

## Quick Wins

1. Upgrade all workflows to `actions/github-script@v7`.
2. Add `await` to every REST call.
3. Fix Nightly Decision Desk output passing and close-order logic.
4. Restrict WIP trigger logic to relevant labeled events only.

## Medium-Term Improvements

1. Add pagination support for all issue-list operations.
2. Introduce idempotency checks for comments and generated report issues.
3. Exclude synthetic/system issues from operational queues.
4. Move repeated helper logic (label matching, issue filtering) into reusable scripts/actions.

## Longer-Term Enhancements

1. Add a validation workflow that lint-checks all workflow YAML on pull requests.
2. Add integration tests using a fixture repo or mocked API responses.
3. Introduce metrics (counts, durations, failure rates) in workflow summaries.
