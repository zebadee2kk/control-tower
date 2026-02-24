# Operating System

## Purpose
Prevent scope drift, cost burn, and stalled progress through structured workflow governance.

## Core Rules

### Work Management
- **No work without an issue** - Every task must be tracked
- **Every issue needs:** priority, gate status, budget cap
- **WIP limit:** Maximum 3 items in progress
- **Single source of truth:** GitHub is the control plane

### Workflow States

1. **Intake** - New ideas captured via issue templates
2. **Research** - Investigation and analysis phase
3. **Plan** - Architecture and design decisions
4. **Build** - Implementation work
5. **Validate** - Testing and review
6. **Launch** - Deployment and release
7. **Operate** - Maintenance and iteration

### Decision Gates

Every issue passes through gate checks:

- **gate:allowed** - Proceed freely
- **gate:needs-approval** - Requires explicit decision
- **gate:paused** - On hold pending external factors

### Stop Conditions

Work stops automatically when:
- Budget cap reached
- Scope significantly changes
- Security risk identified
- Dependencies blocked

## Daily Loop (10 minutes)

1. Open the current **Decision Desk** issue
2. Review items awaiting decision
3. For each item: **Approve** / **Defer** / **Request more info**
4. Check for budget alerts
5. Note any blockers

**Do not start new work without creating an issue first.**

## Weekly Loop (30 minutes)

1. Review [Ecosystem Map](ECOSYSTEM_MAP.md)
2. Update repo statuses
3. Re-score priorities based on current context
4. Select 1-3 items for WIP
5. Create next week's Decision Desk issue

## Priority Scoring

- **P0** - Critical, blocking other work
- **P1** - High value, clear ROI
- **P2** - Normal priority, sequenced work
- **P3** - Parked, revisit later

## Handoff Standards

When passing work between contexts (Perplexity → VS Code → GitHub):

1. **Context** - Why this matters
2. **Inputs** - What you're working with
3. **Expected outputs** - What success looks like
4. **Constraints** - Limits and boundaries
5. **Decision authority** - Who approves what

## Agent Collaboration (Future)

When AI agents are introduced:

- Agents operate via **labels** and **comments** only
- No direct code or finance modifications
- All actions logged in issue timeline
- Human approval required for escalations

## Anti-Patterns to Avoid

❌ Working outside GitHub tracking  
❌ Starting work before approval  
❌ Exceeding budget without gate  
❌ Committing raw conversation exports  
❌ Tool sprawl without consolidation  
❌ Research loops without decision deadlines  

## Success Metrics

- Decisions take < 5 minutes nightly
- Work progresses without drift
- Cost overruns prevented via gates
- Projects move through defined states
- No context lost between sessions