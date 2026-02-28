# Ecosystem Architecture

*Last Updated: 2026-02-28*  
*Status: **VALIDATED** - All 16 repos scanned, zero assumptions*

---

## Executive Summary

The **zebadee2kk ecosystem** consists of **16 repositories** organized into **5 architectural layers**:

1. **Control Planes** (4) - Domain-specific orchestration
2. **Shared Libraries** (3) - Reusable components & services
3. **Data Vaults** (2) - Context & knowledge storage
4. **Standalone Tools** (3) - Purpose-built utilities
5. **Templates & Config** (2) - Consistency tooling

**Integration Pattern**: Hub-and-spoke via MCP (Model Context Protocol), REST APIs, and Python imports.

**Key Decision**: All repos remain **separate** - integration through well-defined interfaces, not code merging.

---

## Layer 1: Control Planes

### Overview

Control planes are **domain-specific orchestration systems** managing distinct operational areas.

### Architecture

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
│ hamnet  │  │hosting- │  │work-os-     │  │idea-vault         │
│(homelab)│  │ops      │  │control-plane│  │(idea inbox)       │
│         │  │(WebHost)│  │(Lily's)     │  │                   │
└─────────┘  └─────────┘  └─────────────┘  └───────────────────┘
```

### Control Plane Details

| Control Plane | Domain | Purpose | Status | Repos Managed |
|--------------|--------|---------|--------|---------------|
| **[control-tower](https://github.com/zebadee2kk/control-tower)** | Personal Projects | 9pm Decision Desk, GitHub portfolio orchestration | 🟢 Phase 2 | 16 GitHub repos |
| **[hamnet](https://github.com/zebadee2kk/hamnet)** | Home Infrastructure | Config management for homelab (Proxmox VMs, Docker, QNAP NAS, network) | 🟢 Phase 2.2 (Security automation live) | Physical + virtual infrastructure |
| **[hosting-ops](https://github.com/zebadee2kk/hosting-ops)** | WebHost365 Business | Customer hosting operations & VPS management | 🟢 Active | Business operations (webhost365.co.uk) |
| **[work-os-control-plane](https://github.com/zebadee2kk/work-os-control-plane)** | Lily's Work | M365 + AI triage for corporate work | 🟡 New (2 days old) | Separate business entity (richardh-lilys) |

### Why Separate Control Planes?

**Rationale**: Each control plane manages a **different operational domain** with distinct:
- **Stakeholders** (personal vs business vs family)
- **Security requirements** (home network vs cloud vs corporate)
- **Operational constraints** (uptime, cost, compliance)
- **Data sensitivity** (personal projects vs customer data vs work data)

**Example**: You wouldn't want to manage your home Proxmox VMs using the same system that manages customer hosting (different failure domains, security zones, and business logic).

---

## Layer 2: Shared Libraries

### Overview

Shared libraries provide **reusable components** consumed by control planes and other projects.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Shared Services Layer                     │
├───────────────────┬──────────────────┬──────────────────────┤
│ ai-cost-tracker   │ zebra-ecosystem  │ ai-powertools        │
│ (Service/API)     │ (Framework)      │ (Component Lib)      │
│ - Usage tracking  │ - Security zones │ - 64 components      │
│ - Notifications   │ - Model registry │ - Modular install    │
│ - Dashboard       │ - Cost patterns  │ - Public tool        │
└───────────────────┴──────────────────┴──────────────────────┘
         ↑ REST API        ↑ Python import      ↑ pip install
    ┌────┴─────┬───────────┴──────┬──────────────┴──────┐
    │          │                  │                     │
┌───▼────┐ ┌──▼───────┐  ┌───────▼──────┐  ┌──────────▼────┐
│control │ │  hamnet  │  │ hosting-ops  │  │ other projects│
│tower   │ │          │  │              │  │               │
└────────┘ └──────────┘  └──────────────┘  └───────────────┘
```

### Library Details

| Library | Type | Maturity | Purpose | Integration |
|---------|------|----------|---------|-------------|
| **[ai-cost-tracker](https://github.com/zebadee2kk/ai-cost-tracker)** | **Production Service** | 🟢 Phase 3 Sprint 2 (121+ tests, CI/CD) | Token/cost tracking, notification system (email, Slack, Discord, Teams) | **REST API** - Deploy as Docker service |
| **[zebra-ecosystem](https://github.com/zebadee2kk/zebra-ecosystem)** | **Framework** | 🟡 Phase 0 (foundation) | Monorepo: 3-zone security model, model registry (15 AI models), cost patterns | **Python import** - `pip install -e .` |
| **[ai-powertools](https://github.com/zebadee2kk/ai-powertools)** | **Component Library** | ⚠️ Research phase (scaffolding only) | 64 modular AI components (routing, memory, orchestration) | **pip install** - `powertools[router]` |

### Integration Strategies

#### 1. ai-cost-tracker (REST API Pattern)

**Why**: Centralized tracking service, single source of truth for all AI costs.

```python
# In control-tower
import requests

AI_COST_TRACKER_URL = os.getenv("AI_COST_TRACKER_URL", "http://localhost:5000")
AI_COST_TRACKER_TOKEN = os.getenv("AI_COST_TRACKER_TOKEN")

def log_ai_usage(provider: str, tokens: int, cost: float, context: dict):
    """Log AI usage to centralized cost tracker"""
    response = requests.post(
        f"{AI_COST_TRACKER_URL}/api/usage",
        json={
            "account_id": "control-tower-prod",
            "service": provider,
            "tokens": tokens,
            "cost": cost,
            "metadata": context
        },
        headers={"Authorization": f"Bearer {AI_COST_TRACKER_TOKEN}"},
        timeout=5
    )
    response.raise_for_status()
    return response.json()
```

#### 2. zebra-ecosystem (Python Import Pattern)

**Why**: Shared patterns and utilities, local execution (no network dependency).

```python
# In control-tower
from zebra_core.models import ModelRegistry
from zebra_core.cost import CostTracker
from zebra_core.config import SecurityZone
from zebra_core.logging import get_logger

logger = get_logger(__name__)

# Select best model for task
registry = ModelRegistry()
model = registry.select_best(
    task="code_generation",
    security_zone=SecurityZone.ZONE_2,  # Local only
    budget=0.10
)

logger.info(f"Selected model: {model.name}")

# Use model and track cost
with CostTracker() as tracker:
    result = model.generate(prompt="Write a Python function")
    tracker.log_usage(
        provider=model.provider,
        tokens=result.tokens,
        cost=result.cost
    )
```

#### 3. ai-powertools (Future Public Library)

**Status**: Currently scaffolding only. Decision pending on merge with zebra-ecosystem.

**If kept separate** (public library):
```bash
pip install ai-powertools[router,memory,guard]
```

```python
from powertools.router import LLMRouter
from powertools.memory import ConversationMemory
from powertools.guard import SafetyCheck

router = LLMRouter()
memory = ConversationMemory()
guard = SafetyCheck()
```

---

## Layer 3: Data Vaults

### Overview

Data vaults store **historical context and knowledge** for AI agents and analysis.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Vaults Layer                         │
├───────────────────────────────┬─────────────────────────────┤
│ project-echo-vault-local      │ idea-vault                  │
│ (Historical LLM context)      │ (Idea inbox & triage)       │
│ - Years of conversations      │ - Voice notes → text        │
│ - RAG retrieval system        │ - Email parsing             │
│ - Context for AI agents       │ - Auto-categorization       │
└───────────────┬───────────────┴─────────────┬───────────────┘
                │ Context retrieval           │ Route ideas
                │                             │
         ┌──────▼──────────┐         ┌────────▼─────────┐
         │  AI Agents      │         │  control-tower   │
         │  (Jarvis, etc)  │         │  (create issues) │
         └─────────────────┘         └──────────────────┘
```

### Vault Details

| Vault | Purpose | Status | Integration |
|-------|---------|--------|-------------|
| **[project-echo-vault-local](https://github.com/zebadee2kk/project-echo-vault-local)** | Historical LLM conversations (years of data) | 🟢 Active (130KB Python code) | RAG system for context retrieval |
| **[idea-vault](https://github.com/zebadee2kk/idea-vault)** | Idea inbox: voice notes, emails, random thoughts | 🟢 Production-ready | Parse → categorize → route to control-tower |

### Integration Pattern

**project-echo-vault-local** (Context Retrieval):
```python
# Future integration
from echo_vault import ContextRetriever

retriever = ContextRetriever()
context = retriever.search(
    query="previous decisions about architecture",
    limit=5,
    min_relevance=0.7
)

for conversation in context:
    print(f"Date: {conversation.date}")
    print(f"Summary: {conversation.summary}")
```

**idea-vault** (Idea Routing):
```python
# In control-tower - Phase 3C
from idea_vault import IdeaParser

parser = IdeaParser()
ideas = parser.fetch_new_ideas()  # Voice notes, emails, etc.

for idea in ideas:
    if idea.is_actionable:
        # Create GitHub issue in appropriate repo
        create_issue(
            repo=idea.suggested_repo,
            title=idea.title,
            body=idea.description,
            labels=["from-idea-vault", idea.category]
        )
```

---

## Layer 4: Standalone Tools

### Overview

Standalone tools provide **specialized capabilities** without being part of control planes.

### Tool Details

| Tool | Purpose | Status | Integration |
|------|---------|--------|-------------|
| **[portfolio-management](https://github.com/zebadee2kk/portfolio-management)** | GitHub repo scanning, prioritization, dependency analysis | 📋 Research complete (26KB MCP plan) | **MCP Server** - control-tower calls via MCP |
| **[secure-claude-orchestrator](https://github.com/zebadee2kk/secure-claude-orchestrator)** | Sandbox for Claude Code CLI (safety wrapper) | 🟢 Active | Standalone - manual execution |
| **[kynee](https://github.com/zebadee2kk/kynee)** | Portable security assessment platform | 🔵 Future project (backlog) | N/A - not started |

### portfolio-management Integration

**Key Finding**: portfolio-management has **substantial planning** (26KB MCP integration document). It will expose **MCP servers** that control-tower consumes.

**Architecture**:
```
control-tower (MCP Client)
     ↓ MCP calls
portfolio-management (MCP Server)
     ├─ Scanner Server (scan repos)
     ├─ Priority Server (rank projects)
     ├─ Dependency Server (analyze dependencies)
     └─ Recommendations Server (security, best practices)
     ↓ GitHub API
All 16 zebadee2kk repos
```

**Example Integration** (Phase 3B):
```python
# In control-tower
from mcp import Client as MCPClient

portfolio_client = MCPClient("portfolio-scanner")

# Scan entire portfolio
scan_results = await portfolio_client.call_tool(
    "scan_portfolio",
    {"include_private": True, "force_refresh": False}
)

# Get priority recommendations
priorities = await portfolio_client.call_tool(
    "get_priorities",
    {"filters": {"tags": ["security"], "min_health": 60}}
)

# Display in Decision Desk
for project in priorities:
    print(f"{project['name']}: {project['priority_score']}")
    print(f"Reason: {project['priority_reason']}")
```

---

## Layer 5: Templates & Config

### Overview

Templates and configuration repos ensure **consistency** across all projects.

### Repo Details

| Repo | Purpose | Status |
|------|---------|--------|
| **[common-vscode-repo](https://github.com/zebadee2kk/common-vscode-repo)** | Sync VSCode configs across devices | 🟢 Active |
| **[best-practice-repo-template](https://github.com/zebadee2kk/best-practice-repo-template)** | Template for new repos (CI/CD, linting, docs structure) | 🟡 Reference |

---

## Integration Architecture

### Hub-and-Spoke Pattern

**control-tower** acts as the **central hub** for GitHub project management:

```
                    ┌─────────────────────┐
                    │   control-tower     │
                    │   (Central Hub)     │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   GitHub API              MCP calls              REST API
        │                      │                      │
┌───────▼────────┐   ┌─────────▼─────────┐   ┌──────▼────────┐
│ 15 GitHub Repos│   │portfolio-mgmt     │   │ai-cost-tracker│
│ (direct access)│   │(MCP Server)       │   │(Service)      │
└────────────────┘   └───────────────────┘   └───────────────┘
```

### Integration Matrix

| From Repo | To Repo | Method | Purpose |
|-----------|---------|--------|----------|
| control-tower | portfolio-management | MCP | Repo scanning & prioritization |
| control-tower | ai-cost-tracker | REST API | Log AI usage |
| control-tower | zebra-ecosystem | Python import | Model selection, security zones |
| control-tower | idea-vault | REST API (future) | Route ideas to GitHub issues |
| control-tower | GitHub repos | GitHub API | CRUD operations on issues/PRs |
| hamnet | ai-cost-tracker | REST API | Log infrastructure AI usage |
| hamnet | zebra-ecosystem | Python import | Shared patterns |
| hosting-ops | ai-cost-tracker | REST API | Log business AI usage |
| All repos | zebra-ecosystem | Python import | Framework patterns |

---

## Deployment Environments

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed execution environments.

| Component | Runs Where | Execution Model |
|-----------|-----------|------------------|
| control-tower | GitHub Actions | Workflows (scheduled + on-demand) |
| ai-cost-tracker | VPS/Homelab Docker | 24/7 service (Flask API + React dashboard) |
| portfolio-management | VPS/Homelab Docker | MCP server (24/7 service) |
| hamnet | hamnet-mgmt VM | Shell scripts + Ansible (on-demand) |
| hosting-ops | Heart Internet VPS | Python scripts (cron + manual) |
| zebra-ecosystem | Imported library | N/A (library code) |
| idea-vault | TBD | Likely VPS Docker or serverless |
| project-echo-vault-local | Local machine | Retrieval system (on-demand) |

---

## Phase 3 Roadmap

See [PHASE_3_ROADMAP.md](./PHASE_3_ROADMAP.md) for detailed implementation plan.

### Phase 3A: Single-Repo Foundation (2-3 weeks)
**Scope**: control-tower manages its own issues
- Enhanced Decision Desk
- Integration with ai-cost-tracker API
- Import zebra-ecosystem patterns
- Testing infrastructure (80% coverage)
- CI/CD pipeline

### Phase 3B: GitHub Portfolio (4-6 weeks)
**Scope**: control-tower + portfolio-management integration
- portfolio-management builds MCP servers
- control-tower aggregates all 16 repos
- Cross-repo dependency tracking
- Portfolio-wide metrics

### Phase 3C: Ecosystem-Wide (8-12 weeks)
**Scope**: Federation across all control planes
- hamnet integration (infrastructure alerts)
- hosting-ops integration (customer tickets)
- idea-vault routing (auto-create issues)
- project-echo-vault context retrieval

---

## Decision Record

### Merge Decisions

**All repos remain SEPARATE**. No code merging required.

**Rationale**:
1. **Control planes** serve different operational domains
2. **ai-cost-tracker** is a production service (deploy as Docker)
3. **zebra-ecosystem** is a framework (import as library)
4. **portfolio-management** has substantial planning (MCP server)
5. **Data vaults** are data sources, not tools
6. **ai-powertools** decision pending (merge to zebra-ecosystem OR keep separate for public use)

### ai-powertools Decision (Pending)

**Option 1**: Merge → zebra-ecosystem (personal framework consolidation)  
**Option 2**: Keep separate (public component library)  
**Status**: Awaiting decision

---

## References

- [Integration Patterns](./INTEGRATION_PATTERNS.md) - Code examples for all integrations
- [Deployment Guide](./DEPLOYMENT.md) - Where things run and how
- [Phase 3 Roadmap](./PHASE_3_ROADMAP.md) - Detailed implementation plan
- [MCP Integration Plan](./MCP_INTEGRATION_PLAN.md) - MCP usage across ecosystem

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-28  
**Next Review**: Phase 3A completion or 2026-03-15
