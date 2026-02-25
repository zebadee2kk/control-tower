# MCP Integration Plan for Control-Tower

## Executive Summary

Model Context Protocol (MCP) can transform control-tower into a truly AI-native orchestration platform by standardizing how AI assistants interact with GitHub, project data, and cross-repository workflows.

## Why MCP for Control-Tower

### Current Challenge
Control-tower manages multiple projects across repositories, requiring custom integration code for each AI assistant (Claude, ChatGPT, Perplexity) to access project data, issues, and workflows.

### MCP Solution
MCP provides a universal interface that any MCP-compatible AI client can use to:
- Query project status across all repositories
- Access issue tracking and prioritization data
- Read and update project documentation
- Execute cross-repo operations through standardized tool calls

## Recommended MCP Servers

### 1. GitHub MCP Server (Official)
**Repository:** `github/github-mcp-server`  
**Stars:** 24,000+  
**Language:** Go

**Use Cases for Control-Tower:**
- Automated cross-repo issue scanning and prioritization
- Real-time project status queries from any AI assistant
- Standardized PR creation and management workflows
- Repository health monitoring and metrics collection

**Implementation:**
```bash
# Install GitHub MCP Server
go install github.com/github/github-mcp-server@latest

# Configure in control-tower/.mcp/config.json
{
  "mcpServers": {
    "github": {
      "command": "github-mcp-server",
      "args": ["--token-file", ".github/token"],
      "env": {
        "GITHUB_ORG": "zebadee2kk"
      }
    }
  }
}
```

### 2. Filesystem MCP Server
**Repository:** `modelcontextprotocol/servers` (src/filesystem)  
**Use Cases:**
- AI assistants can read/write project documentation
- Access control-tower's local project database
- Update tracking files and manifests

**Configuration:**
```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/control-tower"],
    "env": {}
  }
}
```

### 3. SQLite MCP Server (for Project Database)
**Repository:** `modelcontextprotocol/servers` (src/sqlite)  
**Use Cases:**
- Store project prioritization scores
- Track AI assistant interactions and decisions
- Maintain cross-repo dependency graphs

## Architecture Integration

### Current Control-Tower Flow
```
Claude → Custom GitHub API calls → control-tower scripts → Repositories
```

### With MCP
```
Any MCP Client (Claude/ChatGPT/etc) → MCP Server → control-tower → Repositories
```

### Benefits
1. **Multi-AI Support:** Claude, ChatGPT, Perplexity, and local Ollama models all use the same interface
2. **Reduced Maintenance:** One integration point instead of per-AI custom code
3. **Enhanced Capabilities:** MCP servers expose richer data structures than raw APIs
4. **Offline Capability:** MCP servers can run locally, supporting air-gapped workflows

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Install GitHub MCP Server on control-tower VM
- [ ] Configure MCP for zebadee2kk organization access
- [ ] Test basic repo listing and issue queries
- [ ] Document MCP endpoints in control-tower README

### Phase 2: Core Integration (Week 2)
- [ ] Create custom MCP server for control-tower's project database
- [ ] Implement portfolio scanning via MCP
- [ ] Build MCP-aware prioritization workflows
- [ ] Add filesystem MCP for documentation access

### Phase 3: AI Assistant Integration (Week 3)
- [ ] Configure Claude Desktop with control-tower MCP servers
- [ ] Test cross-repo operations through MCP
- [ ] Create MCP-based automation scripts
- [ ] Validate with portfolio-management integration

### Phase 4: Advanced Features (Week 4)
- [ ] Custom MCP server for cross-repo dependency analysis
- [ ] MCP-based AI assistant routing (which AI for which task)
- [ ] Integration with zebra-ecosystem's model intelligence
- [ ] Real-time project dashboard powered by MCP

## Custom MCP Server: control-tower-mcp

### Purpose
A specialized MCP server that exposes control-tower's project management capabilities as standardized tools.

### Exposed Tools
```python
# Example tool definitions
{
  "tools": [
    {
      "name": "list_active_projects",
      "description": "Get all active projects with priority scores",
      "inputSchema": {"type": "object", "properties": {}}
    },
    {
      "name": "scan_repository",
      "description": "Perform portfolio scan on a repository",
      "inputSchema": {
        "type": "object",
        "properties": {
          "owner": {"type": "string"},
          "repo": {"type": "string"}
        }
      }
    },
    {
      "name": "prioritize_issues",
      "description": "Run AI-powered issue prioritization",
      "inputSchema": {
        "type": "object",
        "properties": {
          "repo": {"type": "string"},
          "criteria": {"type": "array"}
        }
      }
    }
  ]
}
```

### Implementation (Python SDK)
```python
# control-tower-mcp/server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import asyncio

app = Server("control-tower")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_active_projects",
            description="Get all active projects with priority scores",
            inputSchema={"type": "object", "properties": {}}
        ),
        # Additional tools...
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "list_active_projects":
        # Implementation here
        projects = await get_projects_from_db()
        return [TextContent(type="text", text=json.dumps(projects))]
    # Handle other tools...

if __name__ == "__main__":
    asyncio.run(app.run())
```

## Security Considerations

### Token Management
- Store GitHub tokens in Vaultwarden, not in config files
- Use read-only tokens where possible
- Implement per-repository access controls in custom MCP servers

### Air-Gapped Operation
- MCP servers run locally on Proxmox infrastructure
- No external dependencies for critical operations
- Option to disable remote MCP servers for sensitive workflows

## Cost Analysis

### Without MCP
- Custom API integration per AI assistant: ~40 hours development
- Maintenance overhead: ~5 hours/month per integration
- Limited reusability across projects

### With MCP
- Initial MCP setup: ~10 hours
- Custom server development: ~20 hours
- Maintenance: ~2 hours/month (standardized interface)
- Immediate reuse across all AI-native projects

**Time Saved:** ~50% over 6 months  
**Maintenance Reduction:** ~60%

## Success Metrics

1. **Integration Coverage:** 100% of control-tower operations accessible via MCP
2. **Multi-AI Support:** Successfully tested with Claude, ChatGPT, and local Ollama
3. **Response Time:** <500ms for project queries via MCP
4. **Uptime:** 99.5%+ for local MCP servers
5. **Developer Velocity:** 2x faster cross-repo automation development

## References

- [MCP Specification](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [GitHub MCP Server](https://github.com/github/github-mcp-server)
- [MCP Servers Collection](https://github.com/modelcontextprotocol/servers)

## Next Steps

1. **Immediate:** Review this document with AI team (Claude, ChatGPT)
2. **This Week:** Install and test GitHub MCP Server
3. **Next Sprint:** Begin custom control-tower-mcp development
4. **Month 1:** Full MCP integration across portfolio

---

**Document Status:** Ready for Implementation  
**Owner:** Project Manager (AI-assisted)  
**Last Updated:** 2026-02-25  
**Related Issues:** To be created in control-tower/issues
