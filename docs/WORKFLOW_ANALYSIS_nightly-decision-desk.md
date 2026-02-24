# Workflow Analysis: nightly-decision-desk.yml

## Line-by-Line Findings
- L24-32: Queries first 100 open issues only; pulls PRs too unless filtered.
- L38: Uses `steps.query.outputs` directly inside script (invalid in github-script runtime).
- L45-51: Issue creation not awaited.
- L57-63: Only first 10 decision-desk issues considered.
- L66-67: Close loop likely closes newest and keeps oldest depending sort order.

## Critical Bugs
1. Cross-step output handling is broken (blocking).
2. Wrong retention logic can preserve stale reports.
3. Pagination omissions cause silent data loss.

## Security
- Moderate abuse: malicious labeling can inflate desk queue.
- No actor trust checks.

## Reliability
- Deterministic runtime failure risk at report creation step.
- No fallback when query or create fails.

## Recommendation
- Single-script implementation for query+create+cleanup with explicit sorting and idempotency.
