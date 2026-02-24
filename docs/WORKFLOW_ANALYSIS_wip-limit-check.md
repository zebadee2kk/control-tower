# Workflow Analysis: wip-limit-check.yml

## Line-by-Line Findings
- L27-34: Counts all open issues, no pagination, includes PRs.
- L35: Hard-coded `maxWip = 3` (no repository variable).
- L46-63: Mutates triggering issue regardless of whether it entered constrained state.

## Critical Bugs
1. Can block unrelated issue when system limit exceeded.
2. `removeLabel` may 404 if state label not on triggering issue.
3. No `await` on comment/add/remove operations.

## Reliability
- High noisy-failure probability on unlabeled/opened events.
- No debounce/concurrency control.

## Recommendation
- Trigger only when target labels added; verify label presence before mutation; use repo variable for threshold.
