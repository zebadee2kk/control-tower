# Bootstrap Script for Labels & Project

The repository includes an idempotent script to automate the setup of GitHub labels and a Project v2 board:

* **Location:** scripts/bootstrap-labels-project.sh
* **Features:**
	- Ensures all 16 standard labels (with exact names/colors from Issue #1)
	- Creates a GitHub Project v2 board named "Control Tower" if missing
	- Adds custom fields: Priority, Gate, Budget Cap, Spend-to-Date
	- Links all open issues to the project
	- (Manual step) Automation for moving issues to "Done" when closed

**Usage:**

```bash
scripts/bootstrap-labels-project.sh
```

Requires: [gh CLI](https://cli.github.com/) with authentication and jq installed.
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