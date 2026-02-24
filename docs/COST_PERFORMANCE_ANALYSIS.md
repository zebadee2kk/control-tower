# Cost & Performance Analysis

## GitHub Actions Cost Estimate
Assuming ~5s per run for lightweight scripts:
- 10 issues/week: negligible (<20 min/month).
- 100 issues/week: ~80-150 min/month.
- 1000 issues/week: could exceed 600+ min/month from frequent event triggers.

## Performance Constraints
- No pagination causes incorrect business logic before compute costs become dominant.
- Event-driven WIP check scans all open issues repeatedly (O(N) per event).

## Optimizations
1. Use search queries by label to reduce scans.
2. Cache counts in report issue or project field.
3. Convert hot-path checks to scheduled reconciliation.
