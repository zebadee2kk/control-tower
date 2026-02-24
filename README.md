# Control Tower

A GitHub-native control plane for AI-assisted projects.

## Principles
- GitHub is the source of truth.
- Work flows through Issues.
- Decisions happen via gates.
- Costs are controlled with budget caps.
- Raw chats stay local; distilled outputs go here.

## Workflow
Idea → Research → Plan → Build → Validate → Launch

## Safety
Never commit secrets or raw exports.

## Structure

```
control-tower/
├── docs/              # Operating system & governance
├── decisions/         # Decision records
├── gold/              # Distilled conversation outputs
├── workflows/         # Automation configs
└── .github/           # Issue templates & PR templates
```

## Daily Routine
1. Review Decision Desk issue
2. Make yes/no decisions (< 5 minutes)
3. Let workflow progress

## Weekly Routine
1. Update ecosystem map
2. Re-score priorities
3. Select 1-3 WIP items

## Getting Started
1. Review [Operating System](docs/OPERATING_SYSTEM.md)
2. Check [Cost Governance](docs/COST_GOVERNANCE.md)
3. Open your first issue using the templates
4. Create your GitHub Project dashboard

---

**Status:** v1 - Structure established, automation pending