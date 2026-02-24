# Integration Test Plan

## Happy Path
1. Create issue with `state:research`.
2. Move through `state:planning` -> `state:build`.
3. Add `gate:needs-approval` and verify Decision Desk inclusion.
4. Add `state:done`; verify issue closes and state normalized.

## Edge + Negative Matrix
- Multiple state labels on one issue.
- Simultaneous labeling by two actors.
- Empty decision desk night.
- WIP at exactly threshold.
- API 5xx retry simulation.
- Rate-limit response simulation.

## Assertions
- No duplicate desk/report issues per period.
- No stale `state:awaiting-decision` older than 24h.
- No issue in more than one active state label.
