# Decision Desk Execution Trace

## Execution Path
1. Trigger at 21:00 UTC or manual dispatch.
2. Query open issues (`per_page:100`).
3. Filter for `gate:needs-approval` and `state:blocked`.
4. Build markdown report body.
5. Create new Decision Desk issue.
6. Query existing `state:awaiting-decision` issues (`per_page:10`).
7. Close all but one issue.

## Failure Points
- API query failure/rate limit.
- Broken step output reference between query and create steps.
- Incorrect close ordering.
- Non-awaited update/create calls.

## Estimated Runtime
~2-6 seconds nominal; can spike with API retries.
