# State Machine Verification

## Declared States (inferred)
`state:research`, `state:planning`, `state:build`, `state:blocked`, `state:done`, `state:awaiting-decision`, `state:report`

## Verification Result: Fails

## Violations
- Mutual exclusivity not enforced.
- Transition guards not encoded.
- Terminal state (`done`) can coexist with active states.
- No guaranteed path from intake to done.

## Required Fix
Implement explicit transition matrix and automatic cleanup of conflicting labels.
