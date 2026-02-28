# Phase 3 Roadmap

*Last Updated: 2026-02-28*  
*Status: **APPROVED** - Ready to execute*

---

## Executive Summary

Phase 3 transforms control-tower from a **single-repo tool** into an **ecosystem orchestration platform**.

**Timeline**: 12-16 weeks (3 phases)  
**Scope**: 16 repositories, 4 control planes, 3 shared services

**Phases**:
1. **Phase 3A**: Single-Repo Foundation (2-3 weeks) - control-tower manages itself
2. **Phase 3B**: GitHub Portfolio (4-6 weeks) - control-tower + portfolio-management integration
3. **Phase 3C**: Ecosystem-Wide (8-12 weeks) - Federation across all control planes

---

## Current State (Phase 2)

### What Exists

✅ **control-tower**:
- Basic Decision Desk (issue listing)
- GitHub Actions workflow (nightly @ 9pm)
- Manual issue management
- Label automation
- WIP limit checking

✅ **Ecosystem**:
- 16 repositories identified
- ai-cost-tracker in production (121+ tests, CI/CD)
- zebra-ecosystem foundation laid
- hamnet security automation live
- portfolio-management research complete (26KB MCP plan)

### Gaps

❌ **control-tower**:
- No AI-powered analysis
- No cross-repo visibility
- No integration with shared services
- No testing infrastructure
- No CI/CD pipeline

❌ **Ecosystem**:
- Services not deployed (ai-cost-tracker, portfolio-management)
- No integration patterns documented
- No shared libraries imported
- No federation between control planes

---

## Phase 3A: Single-Repo Foundation

**Duration**: 2-3 weeks  
**Scope**: control-tower manages **its own issues only**  
**Goal**: Prove patterns work before expanding

### Objectives

1. ✅ Enhanced Decision Desk (filters, search, bulk actions)
2. ✅ AI-powered issue analysis (summaries, priority scoring)
3. ✅ Integration with ai-cost-tracker API
4. ✅ Import zebra-ecosystem for model selection
5. ✅ Testing infrastructure (pytest, 80% coverage)
6. ✅ CI/CD pipeline (automated testing, security scanning)

### Architecture

```
control-tower (GitHub Actions)
     ├─ Enhanced Decision Desk
     │   ├─ Filter by label, priority, staleness
     │   ├─ Search issues by keyword
     │   ├─ Bulk operations (label, close, assign)
     │   └─ AI-powered analysis
     ├─ Integration with ai-cost-tracker
     │   ├─ Log token usage
     │   ├─ Track costs per workflow
     │   └─ Budget alerts
     ├─ Import zebra-ecosystem
     │   ├─ Model selection (best model for task)
     │   ├─ Security zones (local only)
     │   └─ Structured logging
     └─ Testing & CI/CD
         ├─ Unit tests (pytest)
         ├─ Integration tests (mock GitHub API)
         ├─ Security scanning (Bandit, safety)
         └─ Automated deployment
```

### Deliverables

#### Week 1: Infrastructure

**1. Testing Framework**

```bash
mkdir -p tests/{unit,integration,fixtures}
touch tests/__init__.py
touch tests/conftest.py
```

**File**: `tests/conftest.py`

```python
import pytest
from unittest.mock import MagicMock
from github import Github

@pytest.fixture
def mock_github():
    """Mock GitHub API"""
    mock = MagicMock(spec=Github)
    return mock

@pytest.fixture
def sample_issue():
    """Sample GitHub issue"""
    return {
        "number": 42,
        "title": "Implement feature X",
        "state": "open",
        "labels": ["enhancement", "priority:high"],
        "created_at": "2026-02-01T12:00:00Z",
        "updated_at": "2026-02-20T15:30:00Z",
        "body": "Detailed description of feature X"
    }
```

**File**: `tests/unit/test_decision_desk.py`

```python
import pytest
from src.decision_desk import DecisionDesk

def test_filter_by_label(mock_github, sample_issue):
    """Test filtering issues by label"""
    desk = DecisionDesk(mock_github)
    
    # Setup mock
    mock_github.get_repo().get_issues.return_value = [sample_issue]
    
    # Test
    issues = desk.filter_by_label("priority:high")
    
    assert len(issues) == 1
    assert issues[0]["number"] == 42

def test_ai_analysis(mock_github, sample_issue):
    """Test AI-powered issue analysis"""
    desk = DecisionDesk(mock_github)
    
    analysis = desk.analyze_issue(sample_issue)
    
    assert "summary" in analysis
    assert "priority_score" in analysis
    assert 0 <= analysis["priority_score"] <= 100
```

**2. CI/CD Pipeline**

**File**: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Lint with flake8
        run: |
          flake8 src/ tests/ --max-line-length=100 --exclude=venv
      
      - name: Security check with bandit
        run: |
          bandit -r src/ -ll
      
      - name: Check dependencies with safety
        run: |
          safety check --json
      
      - name: Run tests with pytest
        run: |
          pytest tests/ -v --cov=src --cov-report=term --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
      
      - name: Type check with mypy
        run: |
          mypy src/ --ignore-missing-imports
```

**3. Deploy ai-cost-tracker**

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed steps.

```bash
# On hamnet-mgmt VM
cd /opt/services
git clone https://github.com/zebadee2kk/ai-cost-tracker.git
cd ai-cost-tracker
cp .env.example .env
# Configure .env
docker-compose up -d

# Verify
curl http://localhost:5000/api/health
```

#### Week 2: Enhanced Decision Desk

**1. Filter & Search**

**File**: `src/decision_desk.py`

```python
from typing import List, Dict, Any, Optional
from github import Github
from datetime import datetime, timedelta
import re

class DecisionDesk:
    def __init__(self, github_client: Github, repo_name: str):
        self.github = github_client
        self.repo = github_client.get_repo(repo_name)
    
    def get_issues(
        self,
        labels: Optional[List[str]] = None,
        state: str = "open",
        since: Optional[datetime] = None,
        search_term: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get filtered issues"""
        
        # Fetch from GitHub
        issues = self.repo.get_issues(
            state=state,
            labels=labels,
            since=since
        )
        
        # Convert to dict
        issue_list = [
            {
                "number": issue.number,
                "title": issue.title,
                "labels": [label.name for label in issue.labels],
                "state": issue.state,
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat(),
                "body": issue.body or ""
            }
            for issue in issues
        ]
        
        # Search filter
        if search_term:
            issue_list = [
                issue for issue in issue_list
                if re.search(search_term, issue["title"], re.IGNORECASE)
                or re.search(search_term, issue["body"], re.IGNORECASE)
            ]
        
        return issue_list
    
    def filter_stale_issues(self, days: int = 30) -> List[Dict[str, Any]]:
        """Find issues not updated in N days"""
        cutoff = datetime.now(datetime.timezone.utc) - timedelta(days=days)
        
        issues = self.get_issues()
        stale = [
            issue for issue in issues
            if datetime.fromisoformat(issue["updated_at"]) < cutoff
        ]
        
        return stale
    
    def filter_high_priority(self) -> List[Dict[str, Any]]:
        """Get high priority issues"""
        return self.get_issues(labels=["priority:high", "priority:critical"])
```

**2. AI Analysis**

**File**: `src/ai_analysis.py`

```python
from typing import Dict, Any
from zebra_core.models import ModelRegistry, SecurityZone
from integrations.cost_tracker import cost_tracker
import openai
import os

registry = ModelRegistry()

def analyze_issue(issue: Dict[str, Any]) -> Dict[str, Any]:
    """AI-powered issue analysis"""
    
    # Select model
    model = registry.select_best(
        task="text_analysis",
        security_zone=SecurityZone.ZONE_2,  # Local only
        budget=0.05
    )
    
    # Build prompt
    prompt = f"""
Analyze this GitHub issue and provide:
1. One-sentence summary
2. Priority score (0-100)
3. Recommended action

Title: {issue['title']}
Labels: {', '.join(issue['labels'])}
Body: {issue['body'][:500]}
"""
    
    # Call AI
    response = openai.ChatCompletion.create(
        model=model.name,
        messages=[
            {"role": "system", "content": "You are a project manager analyzing GitHub issues."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    # Track cost
    tokens = response.usage.total_tokens
    cost = tokens * model.cost_per_1k_tokens / 1000
    cost_tracker.log_usage(
        provider=model.provider,
        model=model.name,
        tokens=tokens,
        cost=cost,
        context={"task": "issue_analysis", "issue_number": issue["number"]}
    )
    
    # Parse response
    analysis_text = response.choices[0].message.content
    
    return {
        "issue_number": issue["number"],
        "summary": analysis_text,
        "priority_score": extract_priority_score(analysis_text),
        "recommended_action": extract_action(analysis_text),
        "ai_model": model.name,
        "cost": cost
    }

def extract_priority_score(text: str) -> int:
    """Extract priority score from AI response"""
    import re
    match = re.search(r'priority.*?(\d+)', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 50  # Default

def extract_action(text: str) -> str:
    """Extract recommended action from AI response"""
    lines = text.split('\n')
    for line in lines:
        if 'action' in line.lower():
            return line.strip()
    return "Review and prioritize"
```

#### Week 3: Testing & Documentation

**1. Achieve 80% Test Coverage**

```bash
# Run tests
pytest tests/ --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html

# Identify gaps
pytest tests/ --cov=src --cov-report=term-missing
```

**2. Update Documentation**

- [ ] Update README with Phase 3A features
- [ ] Add usage examples
- [ ] Document AI analysis feature
- [ ] Add troubleshooting guide

**3. Demo & Validation**

```bash
# Run Decision Desk manually
python src/decision_desk.py

# Check output
cat reports/decision-desk-$(date +%Y-%m-%d).md

# Verify cost tracking
curl http://localhost:5000/api/summary/daily?account_id=control-tower-prod
```

### Success Metrics

- [ ] 80% test coverage
- [ ] CI/CD pipeline passing
- [ ] ai-cost-tracker integrated and tracking costs
- [ ] Enhanced Decision Desk generates nightly reports
- [ ] AI analysis provides actionable insights
- [ ] Zero security findings from Bandit

### Decision Point

**Proceed to Phase 3B if**:
✅ All success metrics met  
✅ Decision Desk runs reliably for 1 week  
✅ AI analysis provides value (manual validation)  
✅ Cost tracking works correctly

---

## Phase 3B: GitHub Portfolio

**Duration**: 4-6 weeks  
**Scope**: control-tower + portfolio-management integration  
**Goal**: Manage all 16 repos from Decision Desk

### Objectives

1. ✅ Deploy portfolio-management MCP servers
2. ✅ Integrate MCP client in control-tower
3. ✅ Aggregate all 16 repos in Decision Desk
4. ✅ Cross-repo dependency tracking
5. ✅ Portfolio-wide metrics dashboard
6. ✅ Automated prioritization across repos

### Architecture

```
control-tower (GitHub Actions)
     ↓ MCP client calls
portfolio-management (MCP Server)
     ├─ Scanner Server
     │   ├─ Scan all 16 repos
     │   ├─ Cache results (6 hours TTL)
     │   └─ Health scoring
     ├─ Priority Server
     │   ├─ Rank projects by urgency
     │   ├─ Explain priority reasons
     │   └─ Suggest next actions
     ├─ Dependency Server
     │   ├─ Build dependency graph
     │   ├─ Find circular deps
     │   └─ Impact analysis
     └─ Recommendations Server
         ├─ Security audit
         ├─ Best practices check
         └─ Consolidation suggestions
     ↓ GitHub API
All 16 zebadee2kk repos
```

### Deliverables

#### Weeks 1-2: portfolio-management MCP Servers

**Follow the 26KB MCP integration plan** in portfolio-management repo:

1. Build Scanner Server
2. Build Priority Server
3. Build Dependency Server
4. Build Recommendations Server
5. Test with MCP Inspector
6. Deploy to homelab/VPS

**Refer to**:
- [portfolio-management MCP Integration Plan](https://github.com/zebadee2kk/portfolio-management/blob/main/docs/research/MCP_INTEGRATION_PLAN.md)
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment instructions

#### Weeks 3-4: control-tower MCP Integration

**1. Install MCP Client**

**File**: `requirements.txt`

```txt
mcp>=1.0.0
```

**2. Implement Portfolio Scanner Client**

See [INTEGRATION_PATTERNS.md](./INTEGRATION_PATTERNS.md) for full code.

**File**: `src/integrations/portfolio_scanner.py`

(Code provided in INTEGRATION_PATTERNS.md)

**3. Update Decision Desk for Multi-Repo**

**File**: `src/decision_desk_v2.py`

```python
import asyncio
from integrations.portfolio_scanner import PortfolioScanner
from typing import List, Dict, Any

async def generate_portfolio_report():
    """Generate portfolio-wide Decision Desk report"""
    
    async with PortfolioScanner("/opt/services/portfolio-management/mcp_servers/scanner_server.py") as scanner:
        # Scan all repos
        repos = await scanner.scan_portfolio(include_private=True)
        
        # Get priorities
        priorities = await scanner.get_priorities()
        
        # Build report
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_repos": len(repos),
            "high_priority_projects": priorities[:5],
            "portfolio_health": calculate_portfolio_health(repos),
            "stale_repos": [r for r in repos if r["health_score"] < 50],
            "recommendations": await get_recommendations(scanner)
        }
        
        return report

def calculate_portfolio_health(repos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate portfolio-wide metrics"""
    total_issues = sum(r["open_issues"] for r in repos)
    avg_health = sum(r["health_score"] for r in repos) / len(repos)
    critical_count = len([r for r in repos if r["health_score"] < 30])
    
    return {
        "total_open_issues": total_issues,
        "average_health_score": round(avg_health, 1),
        "critical_projects": critical_count,
        "grade": "A" if avg_health > 80 else "B" if avg_health > 60 else "C"
    }

async def get_recommendations(scanner: PortfolioScanner) -> List[str]:
    """Get portfolio-wide recommendations"""
    # This will call the Recommendations Server once it's built
    # For now, return placeholder
    return [
        "Consider archiving 2 stale repos with no activity in 6 months",
        "3 repos have outdated dependencies - run security audit",
        "hamnet and hosting-ops could share VPS deployment patterns"
    ]
```

#### Weeks 5-6: Dashboard & Polish

**1. Portfolio Dashboard**

Generate markdown dashboard:

```markdown
# 🏗️ CONTROL TOWER - Portfolio Dashboard

**Date**: 2026-02-28 21:00:00 UTC  
**Total Repos**: 16  
**Portfolio Health**: B (72/100)

---

## 🔴 High Priority Projects

1. **project-echo-vault-local** (Priority: 95)
   - Reason: Security-sensitive, 8 open issues, no commits in 14 days
   - Action: Review and close stale security issues

2. **ai-cost-tracker** (Priority: 88)
   - Reason: Production service, 3 critical bugs, active development
   - Action: Fix bugs #23, #24, #25 before next release

3. **hamnet** (Priority: 82)
   - Reason: Infrastructure backbone, Phase 2.2 in progress
   - Action: Complete security automation testing

---

## 📈 Portfolio Metrics

- Total Open Issues: 87
- Average Health Score: 72/100
- Critical Projects: 2 (health < 30)
- Stale Repos: 4 (no activity in 30+ days)

---

## ⚠️ Recommendations

1. Archive `kynee` (no activity, future project)
2. Merge `ai-powertools` → `zebra-ecosystem` (reduce duplication)
3. Run security audit on 3 repos with outdated dependencies
```

**2. GitHub Issue Creation**

Auto-create issues for critical findings:

```python
def create_priority_issues(priorities: List[Dict[str, Any]]):
    """Create GitHub issues for high-priority items"""
    
    for project in priorities:
        if project["priority_score"] > 90:
            # Create issue in control-tower for tracking
            github.get_repo("zebadee2kk/control-tower").create_issue(
                title=f"⚠️ Urgent: {project['name']} requires attention",
                body=f"""
                Priority Score: {project['priority_score']}
                Reason: {project['priority_reason']}
                Recommended Action: {project['action']}
                
                [View repo]({project['url']})
                """,
                labels=["auto-generated", "priority:critical", "portfolio"]
            )
```

### Success Metrics

- [ ] All 16 repos visible in Decision Desk
- [ ] portfolio-management MCP servers operational
- [ ] Portfolio dashboard generated nightly
- [ ] Dependency graph accurate (manual validation)
- [ ] Automated prioritization matches manual assessment
- [ ] Cross-repo issues auto-created for critical items

### Decision Point

**Proceed to Phase 3C if**:
✅ All success metrics met  
✅ Portfolio view provides value (user feedback positive)  
✅ MCP integration stable for 2 weeks  
✅ No performance issues (scan completes < 5 minutes)

---

## Phase 3C: Ecosystem-Wide

**Duration**: 8-12 weeks  
**Scope**: Federation across all control planes  
**Goal**: Unified view of personal projects, homelab, and business

### Objectives

1. ✅ hamnet integration (infrastructure alerts in Decision Desk)
2. ✅ hosting-ops integration (customer tickets in Decision Desk)
3. ✅ idea-vault routing (auto-create GitHub issues from ideas)
4. ✅ project-echo-vault integration (context retrieval)
5. ✅ Federated Decision Desk (all domains)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              control-tower (Meta Control Plane)              │
│         Federated Decision Desk - All Domains View           │
└───────┬───────────┬──────────────┬──────────────────────────┘
       │                │              │                        │
    REST API        REST API     REST API              Context API
       │                │              │                        │
┌──────▼──────┐  ┌────▼──────┐  ┌────▼─────┐  ┌────────────▼──────────┐
│    hamnet    │  │ hosting-ops │  │ idea-vault│  │ project-echo-vault   │
│ (infra       │  │ (customer   │  │ (ideas)   │  │ (historical context) │
│  alerts)     │  │  tickets)   │  │           │  │                      │
└─────────────┘  └─────────────┘  └───────────┘  └──────────────────────┘
```

### Deliverables

#### Weeks 1-3: hamnet Integration

**Requirement**: hamnet must expose REST API for alerts.

**New in hamnet**:

**File**: `hamnet/api/alerts_server.py`

```python
from flask import Flask, jsonify
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get infrastructure alerts"""
    
    # Read from audit reports
    with open('/var/log/hamnet-audit/latest-summary.json') as f:
        audit_data = json.load(f)
    
    alerts = []
    
    # Critical findings
    for finding in audit_data.get('critical', []):
        alerts.append({
            "severity": "critical",
            "component": finding['component'],
            "message": finding['message'],
            "timestamp": finding['timestamp']
        })
    
    return jsonify(alerts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

**In control-tower**:

**File**: `src/integrations/hamnet_alerts.py`

```python
import requests
from typing import List, Dict, Any

HAMNET_API_URL = "http://hamnet-mgmt.local:5001"

def get_infrastructure_alerts() -> List[Dict[str, Any]]:
    """Fetch infrastructure alerts from hamnet"""
    
    try:
        response = requests.get(
            f"{HAMNET_API_URL}/api/alerts",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []  # Graceful degradation
```

#### Weeks 4-6: hosting-ops Integration

**Similar to hamnet** - expose REST API for customer tickets.

#### Weeks 7-9: idea-vault Routing

**File**: `src/integrations/idea_router.py`

```python
from idea_vault import IdeaParser
from github import Github

def route_ideas_to_github():
    """Route ideas from idea-vault to GitHub issues"""
    
    parser = IdeaParser()
    ideas = parser.fetch_new_ideas()
    
    github = Github(os.getenv("GITHUB_TOKEN"))
    
    for idea in ideas:
        if idea.is_actionable:
            repo = github.get_repo(idea.suggested_repo)
            repo.create_issue(
                title=idea.title,
                body=f"""
                {idea.description}
                
                ---
                💡 Auto-created from idea-vault
                Source: {idea.source} ({idea.source_type})
                Date: {idea.created_at}
                """,
                labels=["from-idea-vault", idea.category]
            )
```

#### Weeks 10-12: Federated Dashboard

**Unified view across all domains**:

```markdown
# 🏗️ CONTROL TOWER - Federated Decision Desk

**Date**: 2026-02-28 21:00:00 UTC

---

## 💻 GitHub Projects (16 repos)

- High Priority: 5 projects
- Portfolio Health: B (72/100)
- Total Open Issues: 87

---

## 🏠 Homelab Infrastructure (hamnet)

- Status: Healthy
- Active Alerts: 2 (both informational)
- Last Security Scan: 2026-02-28 02:00 UTC

---

## 💼 Business Operations (hosting-ops)

- Customer Tickets: 3 open
- Critical: 1 (downtime reported)
- Response Time: 12 minutes (target: 15 minutes)

---

## 💡 Ideas Queue (idea-vault)

- New Ideas: 7
- Routed to GitHub: 4
- Pending Review: 3
```

### Success Metrics

- [ ] Federated dashboard shows all domains
- [ ] hamnet alerts visible in Decision Desk
- [ ] hosting-ops tickets triaged automatically
- [ ] idea-vault ideas routed to correct repos
- [ ] project-echo-vault provides context for decisions
- [ ] Unified view provides actionable insights

---

## Timeline Summary

| Phase | Duration | Cumulative | Key Deliverable |
|-------|----------|------------|------------------|
| **3A** | 2-3 weeks | 3 weeks | control-tower manages itself |
| **3B** | 4-6 weeks | 9 weeks | All 16 repos in Decision Desk |
| **3C** | 8-12 weeks | 21 weeks | Federated across all domains |

**Total**: 12-16 weeks (3-5 months)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| portfolio-management MCP servers not ready | Medium | High | Start building in parallel during Phase 3A |
| hamnet/hosting-ops APIs not available | Medium | Medium | Build REST API wrappers in those repos |
| AI costs exceed budget | Low | Medium | Budget alerts + fallback to simpler models |
| GitHub API rate limits | Low | High | Aggressive caching, token rotation |
| MCP integration complexity | Medium | High | Follow official MCP examples, start simple |

---

## Success Criteria

**Phase 3 Complete When**:

✅ control-tower Decision Desk runs nightly without failures  
✅ All 16 repos visible and manageable  
✅ AI analysis provides actionable insights  
✅ Cost tracking works across all repos  
✅ portfolio-management MCP servers operational  
✅ Federated view shows GitHub + homelab + business  
✅ 80%+ test coverage maintained  
✅ Documentation complete and accurate

---

## Next Steps (After Phase 3)

**Phase 4: Autonomous Operations** (Future)

- AI agents (Jarvis) handle routine tasks
- Self-healing infrastructure
- Predictive issue detection
- Automated dependency updates
- AI-driven project prioritization

---

## References

- [Ecosystem Architecture](./ECOSYSTEM_ARCHITECTURE.md) - System design
- [Integration Patterns](./INTEGRATION_PATTERNS.md) - Code examples
- [Deployment Guide](./DEPLOYMENT.md) - Infrastructure
- [portfolio-management MCP Plan](https://github.com/zebadee2kk/portfolio-management/blob/main/docs/research/MCP_INTEGRATION_PLAN.md)

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-28  
**Status**: **APPROVED** - Ready to execute Phase 3A  
**Next Review**: Phase 3A completion (Week 3)
