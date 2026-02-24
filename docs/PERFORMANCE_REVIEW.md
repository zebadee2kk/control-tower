# Performance & Efficiency Review

**Date:** 2026-02-25

## API Call Efficiency

### `label-automation.yml`
- Typical run: 0-1 API call.
- Efficient and low overhead.

### `nightly-decision-desk.yml`
- Typical run: 3 list/create/update sequences.
- Could exceed expected calls if many old desks are open.
- No pagination means incomplete data at high issue counts.

### `wip-limit-check.yml`
- Calls `listForRepo` (up to 100 issues) on many issue events.
- Highest unnecessary load due to broad trigger matrix.
- Potentially noisy on active repositories.

### `weekly-cost-rollup.yml`
- Single repository list call + create call.
- No pagination may improve speed but at cost of correctness.

## Rate-Limit Risk

- Likely under 50 calls/run in normal state.
- Risk increases with repeated event triggers and repeated comments in WIP workflow.

## Optimization Suggestions

1. Add event guards so WIP checks run only when relevant labels are added.
2. Use pagination (`paginate` helper or explicit page loop) where full data is required.
3. Add de-duplication guards to prevent duplicate comments.
4. Await each GitHub API call to reduce retries/partial failures.
