# AI Safety Analysis

## Risk Questions
- Permission escalation: possible via maintainer-mediated label actions.
- Infinite loops: possible through repeated label churn and comment spam.
- Budget overrun detection: weak due to brittle parsing.
- Instruction tampering: workflow files insufficiently protected.

## Safeguards Needed
1. Protected workflow paths with mandatory review.
2. Max-action-per-issue-per-hour guardrail.
3. Budget anomaly alerts.
4. Human override command (`/pause-automation`).
