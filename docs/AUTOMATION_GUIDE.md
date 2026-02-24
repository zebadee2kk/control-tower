# Automation Guide

## Overview

This repository currently uses four GitHub Actions workflows:

1. **Label Automation** (`label-automation.yml`)
2. **Nightly Decision Desk** (`nightly-decision-desk.yml`)
3. **WIP Limit Check** (`wip-limit-check.yml`)
4. **Weekly Cost Rollup** (`weekly-cost-rollup.yml`)

## Workflow Matrix

| Workflow | Trigger | Primary Outcome |
|---|---|---|
| Label Automation | Issue labeled/closed + manual dispatch | Auto-close done issues, normalize done label, approval comment |
| Nightly Decision Desk | Daily cron 21:00 UTC + manual dispatch | Generate decision summary issue and close older desks |
| WIP Limit Check | Issue events + manual dispatch | Enforce max 3 in `state:build` and `state:research` |
| Weekly Cost Rollup | Weekly cron Sunday 18:00 UTC + manual dispatch | Create budget/cost rollup report issue |

## Required Labels

- `state:done`
- `gate:needs-approval`
- `state:blocked`
- `state:build`
- `state:research`
- `state:awaiting-decision`
- `state:report`
- `cost:rollup`
- `p0`

## Operational Notes

- Prefer testing with `workflow_dispatch` before relying on schedule/event automation.
- Keep label taxonomy synchronized; missing labels can cause 404/422 API errors.
- Monitor run logs after each rollout or workflow edit.
