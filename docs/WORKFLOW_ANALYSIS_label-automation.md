# Workflow Analysis: label-automation.yml

## Line-by-Line Findings
- L24-33: Closing on `state:done` is correct intent, but call lacks `await`.
- L36-48: Adds `state:done` on close, but does not normalize other state labels.
- L51-60: Gate comment can spam repeatedly when label toggled.

## Bugs
1. Missing `await` on all API mutations.
2. No dedupe for Decision Desk comment.
3. No label exclusivity enforcement.

## Security
- Low direct injection risk; static comment text.
- Moderate integrity risk: any actor who can label can trigger close.

## Reliability
- Non-awaited promises can be dropped on step termination.
- No retry or catch branches.

## Recommendation
- Add awaited calls, idempotency checks, and state-label normalization helper.
