# Integration Patterns

*Last Updated: 2026-02-28*  
*Companion to: [ECOSYSTEM_ARCHITECTURE.md](./ECOSYSTEM_ARCHITECTURE.md)*

---

## Overview

This document provides **code examples** for integrating control-tower with the ecosystem's shared services and data sources.

**Three Integration Methods**:
1. **REST API** - For services (ai-cost-tracker)
2. **MCP (Model Context Protocol)** - For tools (portfolio-management)
3. **Python Import** - For libraries (zebra-ecosystem)

---

## Pattern 1: REST API Integration (ai-cost-tracker)

### Use Case

Track AI token usage and costs across all control planes in a **centralized dashboard**.

### Architecture

```
control-tower (Python)
     ↓ HTTP POST /api/usage
ai-cost-tracker (Flask API)
     ↓ Store in PostgreSQL
React Dashboard (visualization)
```

### Setup

#### 1. Deploy ai-cost-tracker Service

```bash
# On VPS or hamnet
cd /opt/services
git clone https://github.com/zebadee2kk/ai-cost-tracker.git
cd ai-cost-tracker

# Configure environment
cp .env.example .env
nano .env
# Set:
# DATABASE_URL=postgresql://user:pass@localhost/ai_cost_tracker
# SECRET_KEY=<random-secret>
# API_TOKEN=<generate-secure-token>

# Start service
docker-compose up -d

# Verify
curl http://localhost:5000/api/health
# Expected: {"status": "healthy", "database": "connected"}
```

#### 2. Store API Token in GitHub Secrets

```bash
# In control-tower repo settings
gh secret set AI_COST_TRACKER_URL --body "https://ai-cost-tracker.yourdomain.com"
gh secret set AI_COST_TRACKER_TOKEN --body "<token-from-ai-cost-tracker>"
```

### Integration Code

#### control-tower Integration

**File**: `src/integrations/cost_tracker.py`

```python
import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CostTrackerClient:
    """Client for ai-cost-tracker API"""
    
    def __init__(self):
        self.base_url = os.getenv("AI_COST_TRACKER_URL", "http://localhost:5000")
        self.token = os.getenv("AI_COST_TRACKER_TOKEN")
        self.account_id = "control-tower-prod"
        
        if not self.token:
            logger.warning("AI_COST_TRACKER_TOKEN not set - cost tracking disabled")
    
    def log_usage(
        self,
        provider: str,
        model: str,
        tokens: int,
        cost: float,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log AI usage to cost tracker
        
        Args:
            provider: AI provider (e.g., 'openai', 'anthropic', 'perplexity')
            model: Model name (e.g., 'gpt-4', 'claude-3-opus')
            tokens: Total tokens used (input + output)
            cost: Cost in USD
            context: Optional metadata (user, task, repo, etc.)
        
        Returns:
            True if logged successfully, False otherwise
        """
        if not self.token:
            logger.debug("Cost tracking disabled")
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/api/usage",
                json={
                    "account_id": self.account_id,
                    "service": provider,
                    "model": model,
                    "tokens": tokens,
                    "cost": cost,
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": context or {}
                },
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                timeout=5
            )
            response.raise_for_status()
            logger.info(f"Logged usage: {provider}/{model} - {tokens} tokens, ${cost:.4f}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to log usage to cost tracker: {e}")
            return False
    
    def get_daily_summary(self, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get daily cost summary
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
        
        Returns:
            Summary dict or None if error
        """
        if not self.token:
            return None
        
        params = {"account_id": self.account_id}
        if date:
            params["date"] = date
        
        try:
            response = requests.get(
                f"{self.base_url}/api/summary/daily",
                params=params,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch daily summary: {e}")
            return None
    
    def check_budget_alert(self, threshold: float = 10.0) -> bool:
        """Check if monthly spending exceeds threshold
        
        Args:
            threshold: Alert threshold in USD
        
        Returns:
            True if alert should fire, False otherwise
        """
        if not self.token:
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/summary/monthly",
                params={"account_id": self.account_id},
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            monthly_cost = data.get("total_cost", 0)
            
            if monthly_cost > threshold:
                logger.warning(
                    f"Budget alert: Monthly cost ${monthly_cost:.2f} exceeds threshold ${threshold:.2f}"
                )
                return True
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to check budget: {e}")
            return False


# Global instance
cost_tracker = CostTrackerClient()
```

#### Usage Example

**File**: `src/decision_desk.py`

```python
from integrations.cost_tracker import cost_tracker
import openai

def analyze_issue_with_ai(issue_text: str) -> dict:
    """Analyze GitHub issue using AI"""
    
    # Call OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Analyze this GitHub issue"},
            {"role": "user", "content": issue_text}
        ]
    )
    
    # Extract usage
    tokens = response.usage.total_tokens
    cost = tokens * 0.00003  # GPT-4 pricing
    
    # Log to cost tracker
    cost_tracker.log_usage(
        provider="openai",
        model="gpt-4",
        tokens=tokens,
        cost=cost,
        context={
            "task": "issue_analysis",
            "repo": "control-tower",
            "user": "decision_desk_bot"
        }
    )
    
    return response.choices[0].message.content
```

#### GitHub Actions Integration

**File**: `.github/workflows/decision-desk.yml`

```yaml
name: Nightly Decision Desk

on:
  schedule:
    - cron: '0 21 * * *'  # 9 PM daily
  workflow_dispatch:

jobs:
  decision-desk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run Decision Desk
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          AI_COST_TRACKER_URL: ${{ secrets.AI_COST_TRACKER_URL }}
          AI_COST_TRACKER_TOKEN: ${{ secrets.AI_COST_TRACKER_TOKEN }}
        run: python src/decision_desk.py
      
      - name: Check Budget Alert
        run: |
          python -c "
          from integrations.cost_tracker import cost_tracker
          if cost_tracker.check_budget_alert(threshold=10.0):
              print('⚠️ Budget alert triggered!')
              exit(1)
          "
```

---

## Pattern 2: MCP Integration (portfolio-management)

### Use Case

Scan all GitHub repos for health metrics, prioritize projects, and detect dependencies.

### Architecture

```
control-tower (MCP Client)
     ↓ MCP protocol (stdio)
portfolio-management (MCP Server)
     ↓ GitHub API
All zebadee2kk repos
```

### Setup

#### 1. Deploy portfolio-management MCP Server

```bash
# On VPS or hamnet
cd /opt/services
git clone https://github.com/zebadee2kk/portfolio-management.git
cd portfolio-management

# Install MCP SDK
pip install mcp PyGithub gitpython

# Configure
export GITHUB_TOKEN=<your-github-token>

# Test MCP server
python -m mcp_servers.scanner_server
# Should start without errors
```

#### 2. Register MCP Server (Claude Desktop)

**File**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "portfolio-scanner": {
      "command": "python",
      "args": [
        "/opt/services/portfolio-management/mcp_servers/scanner_server.py"
      ],
      "env": {
        "GITHUB_TOKEN": "<your-github-token>"
      }
    }
  }
}
```

### Integration Code

#### control-tower Integration

**File**: `src/integrations/portfolio_scanner.py`

```python
import asyncio
import json
from typing import List, Dict, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import logging

logger = logging.getLogger(__name__)

class PortfolioScanner:
    """Client for portfolio-management MCP server"""
    
    def __init__(self, server_path: str):
        self.server_path = server_path
        self.session: Optional[ClientSession] = None
    
    async def __aenter__(self):
        """Start MCP client session"""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_path],
            env={"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")}
        )
        
        self.stdio, self.write = await stdio_client(server_params)
        self.session = ClientSession(self.stdio, self.write)
        await self.session.__aenter__()
        
        logger.info("Connected to portfolio-management MCP server")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close MCP client session"""
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        logger.info("Disconnected from portfolio-management MCP server")
    
    async def scan_portfolio(
        self,
        include_private: bool = True,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """Scan entire GitHub portfolio
        
        Args:
            include_private: Include private repos
            force_refresh: Bypass cache
        
        Returns:
            List of repo scan results
        """
        result = await self.session.call_tool(
            "scan_portfolio",
            arguments={
                "include_private": include_private,
                "force_refresh": force_refresh
            }
        )
        
        data = json.loads(result.content[0].text)
        logger.info(
            f"Scanned {len(data['results'])} repos "
            f"(cached: {data['cached']})"
        )
        return data["results"]
    
    async def get_priorities(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get prioritized list of projects
        
        Args:
            filters: Optional filters (tags, min_health, etc.)
        
        Returns:
            List of projects sorted by priority
        """
        result = await self.session.call_tool(
            "get_priorities",
            arguments={"filters": filters or {}}
        )
        
        data = json.loads(result.content[0].text)
        logger.info(f"Retrieved {len(data)} prioritized projects")
        return data
    
    async def compare_repos(
        self,
        repo_names: List[str],
        criteria: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Compare multiple repositories
        
        Args:
            repo_names: List of repo names to compare
            criteria: Comparison criteria (activity, health, issues, size)
        
        Returns:
            Comparison results
        """
        result = await self.session.call_tool(
            "compare_repos",
            arguments={
                "repo_names": repo_names,
                "criteria": criteria or ["activity", "health", "issues"]
            }
        )
        
        data = json.loads(result.content[0].text)
        logger.info(f"Compared {len(data)} repositories")
        return data
```

#### Usage Example

**File**: `src/decision_desk.py`

```python
import asyncio
from integrations.portfolio_scanner import PortfolioScanner

async def generate_decision_desk_report():
    """Generate nightly Decision Desk report"""
    
    async with PortfolioScanner("/opt/services/portfolio-management/mcp_servers/scanner_server.py") as scanner:
        # Scan all repos
        repos = await scanner.scan_portfolio(include_private=True)
        
        # Get priorities
        priorities = await scanner.get_priorities(
            filters={
                "tags": ["security", "critical"],
                "min_health": 60
            }
        )
        
        # Generate report
        print("\n📊 DECISION DESK REPORT - 9 PM\n")
        print("=" * 50)
        
        print("\n🔴 HIGH PRIORITY PROJECTS:\n")
        for project in priorities[:5]:
            print(f"- {project['name']} (Priority: {project['priority_score']})")
            print(f"  Reason: {project['priority_reason']}")
        
        print("\n📈 PORTFOLIO HEALTH:\n")
        total_issues = sum(r['open_issues'] for r in repos)
        avg_health = sum(r['health_score'] for r in repos) / len(repos)
        print(f"- Total open issues: {total_issues}")
        print(f"- Average health score: {avg_health:.1f}/100")
        
        # Identify stale repos
        stale_repos = [r for r in repos if r['health_score'] < 50]
        if stale_repos:
            print("\n⚠️ STALE REPOS (needs attention):\n")
            for repo in stale_repos:
                print(f"- {repo['name']} (Health: {repo['health_score']})")

if __name__ == "__main__":
    asyncio.run(generate_decision_desk_report())
```

---

## Pattern 3: Python Import (zebra-ecosystem)

### Use Case

Use shared framework patterns: model selection, security zones, cost tracking, structured logging.

### Architecture

```
control-tower (Python code)
     ↓ from zebra_core import ...
zebra-ecosystem (Installed package)
     ├─ src/zebra_core/models/
     ├─ src/zebra_core/cost/
     ├─ src/zebra_core/config/
     └─ src/zebra_core/logging/
```

### Setup

#### 1. Install zebra-ecosystem as Editable Package

```bash
# Clone zebra-ecosystem
cd ~/projects
git clone https://github.com/zebadee2kk/zebra-ecosystem.git

# Install in editable mode
cd zebra-ecosystem
pip install -e .

# Verify
python -c "from zebra_core.models import ModelRegistry; print('✓ zebra-ecosystem installed')"
```

#### 2. Add to requirements.txt (Development)

**File**: `requirements.txt`

```txt
# Local development
-e /path/to/zebra-ecosystem

# OR use git+ssh for production
git+ssh://git@github.com/zebadee2kk/zebra-ecosystem.git@main
```

### Integration Code

#### Model Selection

**File**: `src/integrations/ai_models.py`

```python
from zebra_core.models import ModelRegistry, SecurityZone
from zebra_core.logging import get_logger

logger = get_logger(__name__)

registry = ModelRegistry()

def select_model_for_task(task: str, budget: float = 0.10) -> dict:
    """Select best AI model for task
    
    Args:
        task: Task type (e.g., 'code_generation', 'analysis', 'summarization')
        budget: Max cost per request in USD
    
    Returns:
        Model configuration dict
    """
    model = registry.select_best(
        task=task,
        security_zone=SecurityZone.ZONE_2,  # Local only, no cloud
        budget=budget
    )
    
    logger.info(
        f"Selected model: {model.name} "
        f"(provider: {model.provider}, cost: ${model.cost_per_1k_tokens:.4f}/1k tokens)"
    )
    
    return {
        "name": model.name,
        "provider": model.provider,
        "endpoint": model.endpoint,
        "max_tokens": model.max_tokens
    }
```

#### Structured Logging

**File**: `src/decision_desk.py`

```python
from zebra_core.logging import get_logger, setup_logging

# Setup at application start
setup_logging(
    level="INFO",
    format="json",  # Structured JSON logs
    output="stdout"
)

logger = get_logger(__name__)

def process_issues():
    logger.info("Starting issue processing", extra={
        "task": "decision_desk",
        "repo_count": 16
    })
    
    try:
        # Process issues...
        logger.info("Processed 42 issues", extra={
            "processed": 42,
            "high_priority": 5,
            "stale": 12
        })
    except Exception as e:
        logger.error("Failed to process issues", extra={
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
```

#### Cost Tracking (Local)

**File**: `src/integrations/local_cost_tracker.py`

```python
from zebra_core.cost import CostTracker
from zebra_core.logging import get_logger

logger = get_logger(__name__)

def track_ai_operation(provider: str, tokens: int, cost: float):
    """Track AI operation using zebra-ecosystem patterns"""
    
    with CostTracker() as tracker:
        tracker.log_usage(
            provider=provider,
            tokens=tokens,
            cost=cost,
            metadata={"source": "control-tower"}
        )
    
    # Also send to centralized ai-cost-tracker
    from integrations.cost_tracker import cost_tracker
    cost_tracker.log_usage(provider, "unknown", tokens, cost)
```

---

## Error Handling Patterns

### Graceful Degradation

```python
from integrations.cost_tracker import cost_tracker
import logging

logger = logging.getLogger(__name__)

def log_ai_usage_safe(provider: str, tokens: int, cost: float):
    """Log AI usage with graceful degradation"""
    
    try:
        # Try centralized tracker first
        if cost_tracker.log_usage(provider, "unknown", tokens, cost):
            return
    except Exception as e:
        logger.warning(f"Failed to log to central tracker: {e}")
    
    # Fallback: log locally
    try:
        from zebra_core.cost import CostTracker
        with CostTracker() as tracker:
            tracker.log_usage(provider, tokens, cost)
    except Exception as e:
        logger.error(f"Failed to log costs: {e}")
    
    # Last resort: just log to file
    logger.info(f"AI usage: {provider} - {tokens} tokens, ${cost:.4f}")
```

### Timeout Handling

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_resilient_session(retries: int = 3, backoff: float = 0.3) -> requests.Session:
    """Create HTTP session with retry logic"""
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Usage
session = create_resilient_session()
response = session.post(
    f"{AI_COST_TRACKER_URL}/api/usage",
    json=payload,
    timeout=5
)
```

---

## Testing Patterns

### Mock External Services

**File**: `tests/test_integrations.py`

```python
import pytest
from unittest.mock import patch, MagicMock
from integrations.cost_tracker import CostTrackerClient

@pytest.fixture
def mock_cost_tracker():
    """Mock ai-cost-tracker API"""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response
        yield mock_post

def test_log_usage(mock_cost_tracker):
    """Test logging AI usage"""
    client = CostTrackerClient()
    result = client.log_usage(
        provider="openai",
        model="gpt-4",
        tokens=1000,
        cost=0.03
    )
    
    assert result is True
    mock_cost_tracker.assert_called_once()
    
    # Verify payload
    call_args = mock_cost_tracker.call_args
    payload = call_args.kwargs['json']
    assert payload['tokens'] == 1000
    assert payload['cost'] == 0.03
```

---

## Configuration Management

### Environment Variables

**File**: `.env.example`

```bash
# AI Cost Tracker
AI_COST_TRACKER_URL=https://ai-cost-tracker.yourdomain.com
AI_COST_TRACKER_TOKEN=<generate-secure-token>

# GitHub
GITHUB_TOKEN=<your-github-token>
GITHUB_OWNER=zebadee2kk

# Portfolio Management
PORTFOLIO_MANAGEMENT_PATH=/opt/services/portfolio-management

# Zebra Ecosystem (if not using editable install)
ZEBRA_ECOSYSTEM_PATH=/path/to/zebra-ecosystem
```

### Secrets Management

```python
import os
from pathlib import Path

def load_secrets():
    """Load secrets from environment or .env file"""
    env_file = Path.home() / ".config" / "control-tower" / ".env"
    
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    required_vars = [
        "GITHUB_TOKEN",
        "AI_COST_TRACKER_TOKEN"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )
```

---

## References

- [Ecosystem Architecture](./ECOSYSTEM_ARCHITECTURE.md) - Overall system design
- [Deployment Guide](./DEPLOYMENT.md) - Where services run
- [Phase 3 Roadmap](./PHASE_3_ROADMAP.md) - Implementation schedule
- [ai-cost-tracker API docs](https://github.com/zebadee2kk/ai-cost-tracker/blob/main/docs/API.md)
- [MCP Protocol](https://modelcontextprotocol.io) - Official MCP documentation

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-28  
**Next Review**: Phase 3A completion
