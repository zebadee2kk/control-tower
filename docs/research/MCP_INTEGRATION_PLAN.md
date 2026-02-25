# Model Context Protocol (MCP) Integration Plan for Control Tower

**Date:** 2026-02-25  
**Status:** Research & Planning Phase  
**Priority:** High  
**Owner:** Project Manager / Architecture Lead

---

## Executive Summary

Control Tower serves as the GitHub-native control plane for AI-assisted projects. MCP enables Control Tower to expose cross-project coordination, issue management, and workflow orchestration as standardized tools that any AI agent (Claude, HeliOS, local models) can consume. This transforms Control Tower from a passive repository manager into an active AI-powered project orchestrator.

---

## What is MCP?

MCP (Model Context Protocol) is an open standard by Anthropic providing a universal interface for AI applications to connect with tools and data sources. Instead of building custom integrations for each AI model, MCP servers expose capabilities that any MCP-compatible client can use.

**Key Benefits for Control Tower:**
- Unified interface for multi-project AI agents
- Standardized GitHub operations across your portfolio
- Cross-repository dependency tracking and coordination
- Natural language project management for all AI models

**MCP Resources:**
- Official Python SDK: https://github.com/modelcontextprotocol/python-sdk (21,827 stars)
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk (11,675 stars)
- Server Examples: https://github.com/modelcontextprotocol/servers
- Documentation: https://modelcontextprotocol.io

---

## How MCP Benefits Control Tower

### 1. Cross-Project Coordination

**Current Challenge:**  
Managing dependencies and coordination between Echo Vault, HeliOS, RedSuite, whoamiAI, and other projects requires manual tracking across multiple repositories.

**MCP Solution:**  
Create `control-tower-coordinator-server` exposing:
- `get_project_status(project_name)` - Health check across repositories
- `find_dependencies(repo, depth)` - Map inter-project dependencies
- `sync_issue(source_repo, target_repo, issue_id)` - Cross-link related work
- `get_portfolio_health()` - Overall status dashboard data

**Value:**  
- AI can answer "What's blocking Echo Vault progress?" by analyzing dependencies
- Automatic detection of breaking changes across projects
- Natural language queries like "Show me all repos with open security issues"

### 2. GitHub Automation & Workflow

**Current Challenge:**  
Repeating GitHub operations (creating issues, managing PRs, updating docs) across multiple projects is manual and time-consuming.

**MCP Solution:**  
Create `control-tower-github-server` with tools:
- `create_coordinated_issue(title, body, affected_repos)` - Multi-repo issue creation
- `bulk_label_management(repos, operation, labels)` - Consistent labeling
- `sync_documentation(source_repo, target_repos, doc_path)` - Doc propagation
- `create_milestone_cascade(name, date, repos)` - Coordinated releases

**Value:**  
- "Create issues for MCP integration in all active projects" executed in seconds
- Consistent project structure across portfolio
- Reduced administrative burden

### 3. AI Agent Collaboration Hub

**Current Challenge:**  
Different AI agents (Claude for coding, local models for analysis, Grok for research) operate in silos without awareness of each other's work.

**MCP Solution:**  
Create `control-tower-agent-registry-server` exposing:
- `register_agent(name, capabilities, status)` - Agent discovery
- `claim_task(agent_id, issue_id)` - Work coordination
- `get_agent_activity(agent_id, timeframe)` - Progress tracking
- `find_agent_for_task(task_description)` - Intelligent routing

**Value:**  
- Prevent duplicate work between AI agents
- Task routing based on agent specialization (security tasks → Echo Vault agents)
- Audit trail of AI contributions

### 4. Portfolio Intelligence & Reporting

**Current Challenge:**  
Understanding progress, bottlenecks, and priorities across 15+ repositories requires manual aggregation.

**MCP Solution:**  
Create `control-tower-analytics-server` with:
- `generate_portfolio_report(timeframe, format)` - Executive summaries
- `identify_stale_projects(criteria)` - Find neglected repos
- `predict_completion(project, milestone)` - Timeline forecasting
- `analyze_velocity(repos, period)` - Development speed metrics

**Value:**  
- Weekly AI-generated status reports
- Data-driven project prioritization
- Early warning for projects falling behind

---

## Architecture Integration

### Control Tower as MCP Coordination Layer

```
┌─────────────────────────────────────────────────────────────────────┐
│  Control Tower (GitHub Repository)                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  MCP Server Layer (Python/TypeScript)                         │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐    │  │
│  │  │Coordinator  │ │GitHub Server │ │Agent Registry Server│    │  │
│  │  │   Server    │ │              │ │                     │    │  │
│  │  └─────────────┘ └──────────────┘ └─────────────────────┘    │  │
│  │  ┌─────────────────────────────────────────────────────┐      │  │
│  │  │Analytics Server                                     │      │  │
│  │  └─────────────────────────────────────────────────────┘      │  │
│  └───────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  GitHub API Integration Layer                                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Portfolio Data Store (Issues, Metadata, Agent Registry)      │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
         ↓ MCP Protocol (Unix Socket or Stdio)
┌─────────────────────────────────────────────────────────────────────┐
│  MCP Clients                                                         │
│  ┌──────────────┐ ┌────────────┐ ┌─────────────┐ ┌──────────────┐  │
│  │HeliOS        │ │Echo Vault  │ │Claude       │ │Local Ollama  │  │
│  │Orchestrator  │ │AI Agents   │ │Desktop      │ │Models        │  │
│  └──────────────┘ └────────────┘ └─────────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
         ↓ MCP Protocol
┌─────────────────────────────────────────────────────────────────────┐
│  Project-Specific MCP Servers                                        │
│  ┌──────────────────┐ ┌────────────────┐ ┌────────────────────┐    │
│  │Echo Vault Intel  │ │HeliOS Model    │ │RedSuite Scanner    │    │
│  │Server            │ │Server          │ │Server              │    │
│  └──────────────────┘ └────────────────┘ └────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Insight:**  
Control Tower acts as the **meta-orchestrator** - it coordinates AI agents that themselves consume project-specific MCP servers.

---

## Implementation Roadmap

### Phase 1: Foundation & GitHub Integration (Weeks 1-3)
**Goal:** Basic Control Tower MCP server managing GitHub operations

**Tasks:**
1. Setup MCP Python SDK in Control Tower repo:
   ```bash
   pip install mcp PyGithub python-dotenv
   ```

2. Create `control-tower-github-server`:
   - List all monitored repositories
   - Create/update issues across repos
   - Query issue status and labels
   - Basic error handling

3. Test with MCP Inspector
4. Document configuration (GitHub token, repo list)
5. Create integration tests

**Success Criteria:**
- MCP server can list all portfolio repos
- Can create issues via natural language ("Create bug report in Echo Vault")
- GitHub API rate limits respected

### Phase 2: Cross-Project Coordination (Weeks 4-6)
**Goal:** Dependency tracking and project health monitoring

**Tasks:**
1. Build `control-tower-coordinator-server`:
   - Dependency graph builder (analyze imports, references)
   - Project health scoring (open issues, PR velocity, staleness)
   - Cross-repo issue linking
   - Blocker detection

2. Implement data caching layer (GitHub API is rate-limited)
3. Create background jobs for periodic updates
4. Build notification system for critical events

**Success Criteria:**
- AI can answer "What depends on Echo Vault?"
- Health scores calculated for all projects
- Dependency graph visualization available

### Phase 3: Agent Registry & Collaboration (Weeks 7-9)
**Goal:** AI agents can discover and coordinate with each other

**Tasks:**
1. Build `control-tower-agent-registry-server`:
   - Agent registration API
   - Task claim/release mechanism
   - Activity logging
   - Capability matching

2. Integrate with HeliOS for multi-model orchestration
3. Create agent "heartbeat" system for liveness
4. Build conflict resolution for competing task claims

**Success Criteria:**
- Multiple agents can register and claim tasks
- No duplicate work across agents
- Activity dashboard shows all agent contributions

### Phase 4: Portfolio Analytics (Weeks 10-12)
**Goal:** AI-powered insights and reporting

**Tasks:**
1. Build `control-tower-analytics-server`:
   - Portfolio report generator
   - Velocity tracking
   - Completion prediction models
   - Stale project detection

2. Create report templates (weekly status, quarterly review)
3. Integrate with external analytics (GitHub Insights API)
4. Build alerting for anomalies

**Success Criteria:**
- Weekly reports generated automatically
- Completion predictions accurate within ±20%
- Early warning system catches stalled projects

### Phase 5: Integration Testing & Rollout (Weeks 13-14)
**Goal:** Production-ready multi-project orchestration

**Tasks:**
1. End-to-end testing with all portfolio projects
2. Performance optimization (caching, batching)
3. Security audit (GitHub token management, access control)
4. Documentation and runbooks
5. Gradual rollout to AI agents

**Success Criteria:**
- All portfolio projects consuming Control Tower MCP servers
- Response times <500ms for simple queries, <5s for complex
- Zero security incidents
- User documentation complete

---

## Technical Design

### GitHub Server Implementation

```python
# mcp_servers/github_server/server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
from github import Github
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("control-tower-github")

server = Server("control-tower-github")

# Initialize GitHub client
gh = Github(os.getenv("GITHUB_TOKEN"))

# Portfolio configuration
PORTFOLIO_REPOS = [
    "zebadee2kk/project-echo-vault-local",
    "zebadee2kk/control-tower",
    "zebadee2kk/portfolio-management",
    # ... other repos
]

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_portfolio_repos",
            description="List all repositories in the managed portfolio",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="create_issue",
            description="Create an issue in one or more repositories",
            inputSchema={
                "type": "object",
                "properties": {
                    "repos": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Repository names (e.g., ['project-echo-vault-local'])"
                    },
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": []
                    }
                },
                "required": ["repos", "title", "body"]
            }
        ),
        Tool(
            name="get_repo_status",
            description="Get health and status information for a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    }
                },
                "required": ["repo"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "list_portfolio_repos":
            repos_info = []
            for repo_name in PORTFOLIO_REPOS:
                try:
                    repo = gh.get_repo(repo_name)
                    repos_info.append({
                        "name": repo_name,
                        "description": repo.description,
                        "open_issues": repo.open_issues_count,
                        "stars": repo.stargazers_count,
                        "updated_at": repo.updated_at.isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error fetching {repo_name}: {e}")
            
            return [TextContent(type="text", text=json.dumps(repos_info, indent=2))]
        
        elif name == "create_issue":
            repos = arguments["repos"]
            title = arguments["title"]
            body = arguments["body"]
            labels = arguments.get("labels", [])
            
            created_issues = []
            for repo_name in repos:
                full_name = f"zebadee2kk/{repo_name}" if "/" not in repo_name else repo_name
                try:
                    repo = gh.get_repo(full_name)
                    issue = repo.create_issue(title=title, body=body, labels=labels)
                    created_issues.append({
                        "repo": full_name,
                        "issue_number": issue.number,
                        "url": issue.html_url
                    })
                    logger.info(f"Created issue #{issue.number} in {full_name}")
                except Exception as e:
                    logger.error(f"Failed to create issue in {full_name}: {e}")
                    created_issues.append({"repo": full_name, "error": str(e)})
            
            return [TextContent(type="text", text=json.dumps(created_issues, indent=2))]
        
        elif name == "get_repo_status":
            repo_name = arguments["repo"]
            full_name = f"zebadee2kk/{repo_name}" if "/" not in repo_name else repo_name
            
            repo = gh.get_repo(full_name)
            
            # Calculate health metrics
            issues = repo.get_issues(state="open")
            issue_count = repo.open_issues_count
            
            # Get recent commits
            commits = repo.get_commits()
            recent_commits = list(commits[:5])
            
            status = {
                "repo": full_name,
                "health_score": calculate_health_score(repo),
                "open_issues": issue_count,
                "open_prs": len([i for i in issues if i.pull_request]),
                "last_commit": recent_commits[0].commit.author.date.isoformat() if recent_commits else None,
                "last_updated": repo.updated_at.isoformat(),
                "stars": repo.stargazers_count,
                "forks": repo.forks_count
            }
            
            return [TextContent(type="text", text=json.dumps(status, indent=2))]
    
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    raise ValueError(f"Unknown tool: {name}")

def calculate_health_score(repo) -> float:
    """Calculate 0-100 health score for a repository"""
    score = 100.0
    
    # Penalty for open issues
    score -= min(repo.open_issues_count * 2, 40)
    
    # Penalty for staleness
    days_since_update = (datetime.now() - repo.updated_at).days
    if days_since_update > 30:
        score -= min((days_since_update - 30) * 0.5, 30)
    
    # Bonus for recent activity
    if days_since_update < 7:
        score += 10
    
    return max(0, min(100, score))

if __name__ == "__main__":
    mcp.server.stdio.stdio_server(server)
```

### Configuration Management

```yaml
# config/control_tower.yaml
github:
  token_env: GITHUB_TOKEN
  rate_limit_buffer: 100  # Keep 100 requests in reserve
  cache_ttl_seconds: 300  # 5 minute cache

portfolio:
  repos:
    - name: project-echo-vault-local
      priority: high
      tags: [security, intelligence]
    - name: control-tower
      priority: high
      tags: [infrastructure, coordination]
    - name: portfolio-management
      priority: medium
      tags: [meta, analytics]

mcp_servers:
  github:
    enabled: true
    transport: stdio
  coordinator:
    enabled: true
    transport: stdio
  agent_registry:
    enabled: false  # Phase 3
  analytics:
    enabled: false  # Phase 4

logging:
  level: INFO
  audit_log: /var/log/control-tower/audit.log
```

---

## Integration with Other Projects

### HeliOS Integration

HeliOS (multi-model orchestrator) uses Control Tower to:
- Discover which projects need attention
- Route tasks to specialized agents (Echo Vault for security, etc.)
- Track agent activity and prevent conflicts

**Example Workflow:**
1. User asks HeliOS: "What security issues need attention?"
2. HeliOS queries Control Tower: `get_portfolio_health()` filtered by security tags
3. Control Tower returns list of Echo Vault, RedSuite issues
4. HeliOS delegates to Echo Vault AI agents via their MCP servers
5. Results aggregated and presented to user

### Echo Vault Integration

Echo Vault consumes Control Tower to:
- Register its AI agents and capabilities
- Claim security-related tasks from portfolio
- Report completion status back to Control Tower

### Portfolio Management Integration

Portfolio Management tool uses Control Tower as primary data source:
- Real-time project health metrics
- Dependency graphs
- Agent activity tracking

---

## Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| GitHub API rate limits exceeded | High | High | - Aggressive caching<br>- Request batching<br>- Secondary token rotation |
| Single point of failure for portfolio | Medium | Critical | - High availability deployment<br>- Graceful degradation<br>- Offline mode for agents |
| Security: GitHub token exposure | Low | Critical | - Environment variables only<br>- Token rotation policy<br>- Minimal scope (no write to code) |
| Coordination conflicts (two agents claiming same task) | Medium | Medium | - Atomic claim operations<br>- Lock timeout mechanism<br>- Conflict detection and resolution |
| Performance degradation with large portfolio | Medium | High | - Lazy loading<br>- Background refresh<br>- Query optimization |

---

## Monitoring & Observability

### Dashboards

1. **Portfolio Health Dashboard**
   - Overall health score trend
   - Per-project status cards
   - Recent activity timeline
   - Top blockers across projects

2. **Agent Activity Dashboard**
   - Registered agents and status
   - Task completion rates
   - Average task duration
   - Agent utilization heatmap

3. **MCP Server Metrics**
   - Request rate per server
   - Error rates
   - Response time percentiles
   - GitHub API quota remaining

### Alerts

- Critical: GitHub token about to expire
- High: Portfolio health score drops below 60
- High: Agent crash or unresponsive >30min
- Medium: Project stale (no commits in 30 days)
- Low: MCP server response time >5s

---

## Next Steps for Project Manager

### Immediate Actions (This Week)

1. **Review & Approve Architecture**
   - Validate Control Tower as meta-orchestrator pattern
   - Approve MCP as standard coordination layer
   - Allocate resources for 14-week roadmap

2. **Setup Environment**
   - Generate GitHub personal access token (scope: repo, read:org)
   - Store token in Vaultwarden
   - Document token rotation procedure

3. **Create Project Tracking**
   - GitHub milestones for each phase
   - Issues for individual servers
   - Weekly sync meetings scheduled

### Decision Points

- [ ] Approve Control Tower as central MCP coordination hub?
- [ ] Commit to 14-week implementation timeline?
- [ ] Define portfolio repositories list (currently using placeholder)?
- [ ] Establish success metrics for Phase 1?

### Dependencies

- **Upstream:** MCP Python SDK (external, stable)
- **Peer:** Echo Vault MCP integration (parallel workstream)
- **Downstream:** HeliOS integration (depends on Phase 3)

### Resources Needed

- Python developer (async/await experience) - 1 FTE
- GitHub API expertise - 0.5 FTE
- DevOps for deployment - 0.25 FTE
- GitHub personal access token (fine-grained recommended)

---

## References

1. **MCP Official Resources**
   - Python SDK: https://github.com/modelcontextprotocol/python-sdk
   - TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
   - Documentation: https://modelcontextprotocol.io

2. **Related Control Tower Documents**
   - Architecture: `docs/ARCHITECTURE.md` (TBD)
   - GitHub Integration Guide: `docs/GITHUB_SETUP.md` (TBD)

3. **Cross-Project Integration**
   - Echo Vault MCP Plan: `../project-echo-vault-local/docs/research/MCP_INTEGRATION_PLAN.md` ✓
   - HeliOS MCP Plan: (TBD)
   - Portfolio Management MCP Plan: (TBD)

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-25  
**Next Review:** Upon Phase 1 kickoff or 2026-03-11
