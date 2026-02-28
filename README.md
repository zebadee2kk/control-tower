# Control Tower

**Meta Control Plane for Personal AI-Powered Projects**

[![Phase](https://img.shields.io/badge/Phase-2→3-blue.svg)](docs/PHASE_3_ROADMAP.md)
[![Repos](https://img.shields.io/badge/Repos-16-green.svg)](docs/ECOSYSTEM_ARCHITECTURE.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What Is Control Tower?

Control Tower is the **central orchestration platform** for managing 16 personal GitHub repositories across multiple domains:

- **Personal Projects** (GitHub repos)
- **Homelab Infrastructure** (hamnet)
- **Business Operations** (WebHost365)
- **AI Development** (ai-cost-tracker, zebra-ecosystem)

**Core Feature**: **9pm Decision Desk** - Nightly GitHub Actions workflow that analyzes all projects, prioritizes work, and provides actionable recommendations.

---

## Quick Start

### For New Contributors

1. **Understand the ecosystem**:
   - [Ecosystem Architecture](docs/ECOSYSTEM_ARCHITECTURE.md) - Complete system design
   - [Integration Patterns](docs/INTEGRATION_PATTERNS.md) - How components connect
   - [Deployment Guide](docs/DEPLOYMENT.md) - Where things run

2. **Review current phase**:
   - [Phase 3 Roadmap](docs/PHASE_3_ROADMAP.md) - Implementation plan
   - Currently in **Phase 2** → **Phase 3A** (single-repo foundation)

3. **Set up development environment**:
   ```bash
   git clone https://github.com/zebadee2kk/control-tower.git
   cd control-tower
   pip install -r requirements.txt
   cp .env.example .env
   # Configure .env with your tokens
   ```

4. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

### For AI Assistants

**Start here**: [Ecosystem Architecture](docs/ECOSYSTEM_ARCHITECTURE.md) - Complete validated architecture (zero assumptions).

---

## Principles

- **GitHub is the source of truth** - All work tracked as issues
- **Work flows through gates** - Decision points at each phase
- **Costs are controlled** - Budget caps via ai-cost-tracker
- **Hub-and-spoke integration** - control-tower orchestrates, components specialize
- **Phase discipline** - Complete before advancing

---

## Architecture Overview

### The Ecosystem (16 Repositories)

```
┌─────────────────────────────────────────────────────────────┐
│                   Meta Control Plane                         │
│              control-tower (This Project)                    │
│         9pm Decision Desk - GitHub Portfolio Manager         │
└──────────┬──────────────────────────────────────────────────┘
           │ Orchestrates personal projects
           │
    ┌──────┴──────┬───────────────┬──────────────────────────┐
    │             │               │                          │
┌───▼─────┐  ┌────▼────┐  ┌──────▼──────┐  ┌──────────────▼────┐
│ hamnet  │  │hosting- │  │portfolio-   │  │15 other repos     │
│(homelab)│  │ops      │  │management   │  │                   │
└─────────┘  └─────────┘  └─────────────┘  └───────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Shared Services Layer                           │
├──────────────────┬──────────────────┬──────────────────────┤
│ ai-cost-tracker  │ zebra-ecosystem  │ ai-powertools        │
│ (Service)        │ (Framework)      │ (Components)         │
└──────────────────┴──────────────────┴──────────────────────┘
```

**See**: [Full Architecture](docs/ECOSYSTEM_ARCHITECTURE.md)

---

## Core Features

### Phase 2 (Current)

✅ **Decision Desk** - Nightly issue analysis
✅ **Label Automation** - Auto-apply labels based on rules
✅ **WIP Limits** - Enforce work-in-progress constraints
✅ **Cost Tracking** - Weekly AI cost rollup
✅ **Manual Prioritization** - GitHub Projects board

### Phase 3A (In Progress)

🚧 **Enhanced Decision Desk** - Filters, search, bulk actions
🚧 **AI-Powered Analysis** - Priority scoring, recommendations
🚧 **ai-cost-tracker Integration** - Real-time cost tracking
🚧 **Testing Infrastructure** - 80% coverage, CI/CD pipeline

### Phase 3B (Planned - 4-6 weeks)

📅 **Portfolio Management** - All 16 repos in one view
📅 **MCP Integration** - portfolio-management MCP servers
📅 **Cross-Repo Dependencies** - Dependency tracking
📅 **Automated Prioritization** - AI-driven project ranking

### Phase 3C (Future - 8-12 weeks)

🔮 **Federated Decision Desk** - GitHub + homelab + business
🔮 **hamnet Integration** - Infrastructure alerts
🔮 **idea-vault Routing** - Auto-create issues from ideas
🔮 **Ecosystem-Wide View** - Unified operational dashboard

**See**: [Phase 3 Roadmap](docs/PHASE_3_ROADMAP.md)

---

## Daily Routine

**9:00 PM GMT** - Decision Desk workflow runs automatically:

1. Scan control-tower issues (Phase 3A)
2. Analyze with AI (priority scoring, recommendations)
3. Generate Decision Desk report
4. Post summary as GitHub issue
5. Track AI costs to ai-cost-tracker

**Your Action**: Review the Decision Desk issue (< 5 minutes)
- Approve/reject recommendations
- Update priorities
- Close completed issues

---

## Weekly Routine

1. **Review Portfolio Health** - Check ai-cost-tracker dashboard
2. **Re-score Priorities** - Adjust based on new information
3. **Select 1-3 WIP Items** - Respect WIP limits
4. **Plan Next Week** - Add issues for upcoming work

---

## Project Structure

```
control-tower/
├── docs/                    # Documentation
│   ├── ECOSYSTEM_ARCHITECTURE.md      # ⭐ System design (READ THIS FIRST)
│   ├── INTEGRATION_PATTERNS.md        # Code examples for integrations
│   ├── DEPLOYMENT.md                  # Where things run
│   ├── PHASE_3_ROADMAP.md             # Implementation plan
│   ├── OPERATING_SYSTEM.md            # Operating principles
│   └── COST_GOVERNANCE.md             # Budget management
├── src/                     # Source code
│   ├── decision_desk.py               # Core Decision Desk logic
│   ├── integrations/                  # External service clients
│   │   ├── cost_tracker.py            # ai-cost-tracker API
│   │   ├── portfolio_scanner.py       # portfolio-management MCP
│   │   └── hamnet_alerts.py           # hamnet REST API
│   └── ai_analysis.py                 # AI-powered issue analysis
├── tests/                   # Test suite
│   ├── unit/                          # Unit tests
│   ├── integration/                   # Integration tests
│   └── fixtures/                      # Test data
├── scripts/                 # Automation scripts
│   ├── bootstrap-labels-project.sh    # Setup labels & project board
│   └── deployment/                    # Deployment automation
├── .github/                 # GitHub automation
│   ├── workflows/                     # GitHub Actions
│   │   ├── nightly-decision-desk.yml  # 9pm workflow
│   │   ├── ci.yml                     # CI/CD pipeline
│   │   └── weekly-cost-rollup.yml     # Cost reporting
│   └── ISSUE_TEMPLATE/                # Issue templates
├── decisions/               # Decision records (TBD)
├── gold/                    # Distilled conversation outputs (TBD)
└── README.md               # This file
```

---

## Integration with Ecosystem

### ai-cost-tracker (REST API)

**Purpose**: Track AI token usage and costs across all repos.

```python
from integrations.cost_tracker import cost_tracker

cost_tracker.log_usage(
    provider="openai",
    model="gpt-4",
    tokens=1000,
    cost=0.03
)
```

**See**: [Integration Patterns - REST API](docs/INTEGRATION_PATTERNS.md#pattern-1-rest-api-integration-ai-cost-tracker)

### portfolio-management (MCP)

**Purpose**: Scan all GitHub repos, prioritize projects, analyze dependencies.

```python
from integrations.portfolio_scanner import PortfolioScanner

async with PortfolioScanner(path) as scanner:
    repos = await scanner.scan_portfolio()
    priorities = await scanner.get_priorities()
```

**See**: [Integration Patterns - MCP](docs/INTEGRATION_PATTERNS.md#pattern-2-mcp-integration-portfolio-management)

### zebra-ecosystem (Python Import)

**Purpose**: Shared framework for model selection, security zones, cost patterns.

```python
from zebra_core.models import ModelRegistry
from zebra_core.config import SecurityZone

registry = ModelRegistry()
model = registry.select_best(
    task="code_generation",
    security_zone=SecurityZone.ZONE_2,
    budget=0.10
)
```

**See**: [Integration Patterns - Python Import](docs/INTEGRATION_PATTERNS.md#pattern-3-python-import-zebra-ecosystem)

---

## Deployment

| Component | Runs Where | How |
|-----------|-----------|-----|
| **control-tower** | GitHub Actions | Scheduled workflows (9pm daily) |
| **ai-cost-tracker** | VPS/Homelab Docker | Flask API + React dashboard |
| **portfolio-management** | VPS/Homelab Docker | MCP server (stdio) |
| **hamnet** | hamnet-mgmt VM | Shell scripts + Ansible |

**See**: [Deployment Guide](docs/DEPLOYMENT.md)

---

## Bootstrap Script for Labels & Project

The repository includes an idempotent script to automate the setup of GitHub labels and a Project v2 board:

* **Location:** `scripts/bootstrap-labels-project.sh`
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

**Requires**: [gh CLI](https://cli.github.com/) with authentication and `jq` installed.

---

## Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### CI/CD Pipeline

**GitHub Actions** automatically runs on:
- Push to `main` or `develop`
- Pull requests

**Pipeline Steps**:
1. Lint (flake8)
2. Security scan (Bandit, safety)
3. Type check (mypy)
4. Test (pytest with coverage)
5. Upload coverage to Codecov

---

## Contributing

Contributions are welcome! Please:

1. **Read the docs**: Start with [Ecosystem Architecture](docs/ECOSYSTEM_ARCHITECTURE.md)
2. **Create an issue**: Describe the feature or bug
3. **Fork & branch**: Create a feature branch
4. **Write tests**: Maintain 80%+ coverage
5. **Submit PR**: Reference the issue number

---

## Documentation

### Essential Reading

| Document | Purpose |
|----------|----------|
| [Ecosystem Architecture](docs/ECOSYSTEM_ARCHITECTURE.md) | **START HERE** - Complete system design |
| [Integration Patterns](docs/INTEGRATION_PATTERNS.md) | Code examples for all integrations |
| [Deployment Guide](docs/DEPLOYMENT.md) | Where things run and how to deploy |
| [Phase 3 Roadmap](docs/PHASE_3_ROADMAP.md) | Implementation timeline (12-16 weeks) |
| [Operating System](docs/OPERATING_SYSTEM.md) | Operating principles & workflow |
| [Cost Governance](docs/COST_GOVERNANCE.md) | Budget management & alerts |
| [MCP Integration Plan](docs/MCP_INTEGRATION_PLAN.md) | Model Context Protocol usage |

### Additional Docs

- [Ecosystem Map](docs/ECOSYSTEM_MAP.md) - Repository relationships
- [Testing Plan](docs/TESTING_PLAN.md) - Test strategy
- [Security Review](docs/SECURITY_REVIEW.md) - Security considerations
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues

---

## FAQ

### What's the relationship with hamnet?

hamnet manages **physical infrastructure** (Proxmox VMs, Docker, network), control-tower manages **GitHub projects**. They integrate via REST API in Phase 3C.

### What's the relationship with ai-cost-tracker?

ai-cost-tracker is a **shared service** that control-tower (and all other projects) call via REST API to track AI token usage and costs.

### What's the relationship with portfolio-management?

portfolio-management provides **MCP servers** that control-tower calls to scan repos, prioritize projects, and analyze dependencies.

### What's the difference between control-tower and zebra-ecosystem?

control-tower is a **control plane** (orchestration), zebra-ecosystem is a **framework** (shared patterns). control-tower imports zebra-ecosystem for model selection, security zones, etc.

**See**: [Ecosystem Architecture](docs/ECOSYSTEM_ARCHITECTURE.md) for complete relationships.

---

## Success Metrics

**Phase 3A Complete**:
- ✅ Decision Desk runs nightly without failures
- ✅ 80% test coverage achieved
- ✅ ai-cost-tracker tracking all AI usage
- ✅ CI/CD pipeline passing
- ✅ Enhanced Decision Desk provides value

**Phase 3B Complete**:
- ✅ All 16 repos visible in Decision Desk
- ✅ portfolio-management MCP servers operational
- ✅ Cross-repo dependencies tracked
- ✅ Automated prioritization matches manual assessment

**Phase 3C Complete**:
- ✅ Federated view (GitHub + homelab + business)
- ✅ hamnet alerts visible in Decision Desk
- ✅ idea-vault ideas routed automatically
- ✅ Unified operational dashboard

---

## Roadmap

| Phase | Duration | Status | Key Deliverable |
|-------|----------|--------|------------------|
| Phase 1 | Complete | ✅ | Basic structure & workflows |
| Phase 2 | Complete | ✅ | Decision Desk, labels, WIP limits |
| **Phase 3A** | 2-3 weeks | 🚧 **IN PROGRESS** | Single-repo foundation |
| **Phase 3B** | 4-6 weeks | 📅 Planned | GitHub portfolio (16 repos) |
| **Phase 3C** | 8-12 weeks | 📅 Future | Ecosystem-wide federation |
| Phase 4 | TBD | 🔮 Future | Autonomous operations (AI agents) |

**See**: [Phase 3 Roadmap](docs/PHASE_3_ROADMAP.md)

---

## Contact

- **Owner**: zebadee2kk
- **Repository**: https://github.com/zebadee2kk/control-tower
- **Issues**: [GitHub Issues](https://github.com/zebadee2kk/control-tower/issues)
- **Discussions**: [GitHub Discussions](https://github.com/zebadee2kk/control-tower/discussions)

---

## License

MIT License - See [LICENSE](LICENSE)

---

## Status

**Last Updated**: 2026-02-28  
**Repository Status**: 🟢 Active Development  
**Phase**: 2 → 3A (Single-Repo Foundation)  
**Next Milestone**: Phase 3A completion (3 weeks)

---

**Control Tower** is not just a project manager — it's the **orchestration layer** for a personal AI-powered ecosystem spanning 16 repositories, homelab infrastructure, and business operations.

🏗️ **The future of personal digital operations starts here.**
