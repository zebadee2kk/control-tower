# Deployment Guide

*Last Updated: 2026-02-28*  
*Companion to: [ECOSYSTEM_ARCHITECTURE.md](./ECOSYSTEM_ARCHITECTURE.md)*

---

## Overview

This document specifies **where each component runs** and **how to deploy** them.

**Execution Environments**:
1. **GitHub Actions** - Scheduled workflows (control-tower)
2. **Docker Services** - 24/7 APIs (ai-cost-tracker, portfolio-management)
3. **VMs / Bare Metal** - Infrastructure management (hamnet)
4. **VPS** - Business operations (hosting-ops)
5. **Local Dev** - Development and testing

---

## Deployment Matrix

| Component | Runs Where | Execution Model | Database | Backup |
|-----------|-----------|------------------|----------|--------|
| **control-tower** | GitHub Actions | Workflows (9pm daily + on-demand) | SQLite (GitHub artifacts) | Git commits |
| **ai-cost-tracker** | VPS/Homelab Docker | 24/7 Flask API + React dashboard | PostgreSQL | Daily dumps |
| **portfolio-management** | VPS/Homelab Docker | 24/7 MCP server | SQLite (local cache) | Git commits |
| **hamnet** | hamnet-mgmt VM (Proxmox) | Shell scripts + Ansible (on-demand) | N/A (config files) | Git commits |
| **hosting-ops** | Heart Internet VPS | Python scripts (cron + manual) | TBD | TBD |
| **zebra-ecosystem** | Imported library | N/A (installed via pip) | N/A | Git commits |
| **ai-powertools** | Imported library | N/A (installed via pip) | N/A | Git commits |
| **idea-vault** | TBD (likely VPS Docker) | REST API (future) | PostgreSQL | Daily dumps |
| **project-echo-vault-local** | Local machine | On-demand retrieval | Local files | Manual backup |
| **secure-claude-orchestrator** | Local machine | Manual execution | N/A | N/A |
| **kynee** | N/A (future project) | TBD | TBD | TBD |
| **work-os-control-plane** | TBD (Lily's setup) | TBD | TBD | TBD |

---

## 1. control-tower (GitHub Actions)

### Architecture

```
GitHub Actions Runner (Ubuntu)
     ├─ Workflows triggered by:
     │   ├─ Schedule (cron: 0 21 * * * = 9 PM daily)
     │   ├─ Push to main
     │   └─ Manual trigger (workflow_dispatch)
     ├─ Python 3.11
     ├─ Dependencies from requirements.txt
     └─ Secrets from GitHub Secrets
```

### Deployment Steps

#### 1. Configure GitHub Secrets

```bash
# In control-tower repo
gh secret set GITHUB_TOKEN --body "<your-github-token>"
gh secret set AI_COST_TRACKER_URL --body "https://ai-cost-tracker.yourdomain.com"
gh secret set AI_COST_TRACKER_TOKEN --body "<token-from-ai-cost-tracker>"
```

#### 2. Workflow Configuration

**File**: `.github/workflows/nightly-decision-desk.yml`

```yaml
name: Nightly Decision Desk

on:
  schedule:
    - cron: '0 21 * * *'  # 9 PM UTC daily
  workflow_dispatch:       # Manual trigger

jobs:
  decision-desk:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run Decision Desk
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          AI_COST_TRACKER_URL: ${{ secrets.AI_COST_TRACKER_URL }}
          AI_COST_TRACKER_TOKEN: ${{ secrets.AI_COST_TRACKER_TOKEN }}
        run: |
          python src/decision_desk.py
      
      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: decision-desk-report-${{ github.run_number }}
          path: |
            reports/*.md
            reports/*.json
            logs/*.log
          retention-days: 30
      
      - name: Check Budget Alert
        if: always()
        run: |
          python -c "
          from integrations.cost_tracker import cost_tracker
          import sys
          if cost_tracker.check_budget_alert(threshold=10.0):
              print('⚠️ Budget alert: Monthly AI costs exceed $10')
              sys.exit(1)
          "
```

#### 3. Testing

```bash
# Test workflow locally with act
act -j decision-desk --secret-file .env.local

# Or trigger manually on GitHub
gh workflow run nightly-decision-desk.yml

# Check status
gh run list --workflow=nightly-decision-desk.yml
```

### Storage

- **Artifacts**: Uploaded to GitHub (30-day retention)
- **Logs**: Available in Actions tab
- **State**: No persistent state (stateless execution)

---

## 2. ai-cost-tracker (Docker Service)

### Architecture

```
Docker Compose Stack
     ├─ Flask API (Port 5000)
     ├─ React Dashboard (Port 3000)
     ├─ PostgreSQL (Port 5432, internal)
     └─ Nginx Reverse Proxy (Port 80/443)
```

### Deployment Steps

#### 1. Choose Deployment Target

**Option A**: VPS (Heart Internet, DigitalOcean, etc.)  
**Option B**: Homelab (hamnet-mgmt VM or dedicated Docker host)

**Recommendation**: **Homelab** for Phase 3A (development), migrate to VPS in Phase 3B for reliability.

#### 2. Deploy to Homelab

```bash
# SSH to hamnet-mgmt VM
ssh rham-admin@hamnet-mgmt.local

# Create service directory
sudo mkdir -p /opt/services
cd /opt/services

# Clone repo
sudo git clone https://github.com/zebadee2kk/ai-cost-tracker.git
cd ai-cost-tracker

# Configure environment
sudo cp .env.example .env
sudo nano .env
```

**File**: `.env`

```bash
# Database
DATABASE_URL=postgresql://ai_cost_tracker:SecurePassword123@postgres:5432/ai_cost_tracker

# Security
SECRET_KEY=<generate-with-openssl-rand-hex-32>
API_TOKEN=<generate-with-openssl-rand-hex-32>
ALLOWED_ORIGINS=http://localhost:3000,https://control-tower.yourdomain.com

# Notifications (optional)
SENDGRID_API_KEY=<your-sendgrid-key>
SLACK_WEBHOOK_URL=<your-slack-webhook>

# Application
FLASK_ENV=production
LOG_LEVEL=INFO
```

#### 3. Start Service

```bash
# Build and start
sudo docker-compose up -d

# Check logs
sudo docker-compose logs -f

# Verify health
curl http://localhost:5000/api/health
# Expected: {"status": "healthy", "database": "connected"}

# Access dashboard
open http://localhost:3000
```

#### 4. Configure Reverse Proxy (Optional)

**File**: `/etc/nginx/sites-available/ai-cost-tracker`

```nginx
server {
    listen 80;
    server_name ai-cost-tracker.hamnet.local;
    
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ai-cost-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Maintenance

```bash
# Update service
cd /opt/services/ai-cost-tracker
sudo git pull
sudo docker-compose down
sudo docker-compose up -d --build

# Backup database
sudo docker-compose exec postgres pg_dump -U ai_cost_tracker ai_cost_tracker > backup.sql

# View logs
sudo docker-compose logs -f --tail=100

# Restart
sudo docker-compose restart
```

---

## 3. portfolio-management (MCP Server)

### Architecture

```
MCP Server (Python stdio)
     ├─ Scanner Server (port N/A, stdio)
     ├─ Priority Server (port N/A, stdio)
     ├─ Dependency Server (port N/A, stdio)
     └─ Recommendations Server (port N/A, stdio)

Clients:
     ├─ Claude Desktop (MCP client)
     └─ control-tower (MCP client via Python SDK)
```

### Deployment Steps

#### 1. Install MCP Server

```bash
# On homelab or VPS
cd /opt/services
git clone https://github.com/zebadee2kk/portfolio-management.git
cd portfolio-management

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install mcp PyGithub gitpython

# Test server
export GITHUB_TOKEN=<your-token>
python mcp_servers/scanner_server.py
# Should start without errors (waiting for MCP client connection)
```

#### 2. Register with Claude Desktop

**File**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)  
**File**: `~/.config/Claude/claude_desktop_config.json` (Linux)

```json
{
  "mcpServers": {
    "portfolio-scanner": {
      "command": "/opt/services/portfolio-management/venv/bin/python",
      "args": [
        "/opt/services/portfolio-management/mcp_servers/scanner_server.py"
      ],
      "env": {
        "GITHUB_TOKEN": "<your-github-token>"
      }
    },
    "portfolio-priority": {
      "command": "/opt/services/portfolio-management/venv/bin/python",
      "args": [
        "/opt/services/portfolio-management/mcp_servers/priority_server.py"
      ],
      "env": {
        "GITHUB_TOKEN": "<your-github-token>"
      }
    }
  }
}
```

#### 3. Test MCP Server

```bash
# Using MCP inspector
npx @modelcontextprotocol/inspector python mcp_servers/scanner_server.py

# Or test from control-tower
python -c "
import asyncio
from integrations.portfolio_scanner import PortfolioScanner

async def test():
    async with PortfolioScanner('/opt/services/portfolio-management/mcp_servers/scanner_server.py') as scanner:
        repos = await scanner.scan_portfolio()
        print(f'Scanned {len(repos)} repos')

asyncio.run(test())
"
```

### Maintenance

```bash
# Update MCP server
cd /opt/services/portfolio-management
git pull
source venv/bin/activate
pip install --upgrade mcp PyGithub gitpython

# Clear cache
rm -rf /tmp/portfolio_cache/*

# Test after update
python mcp_servers/scanner_server.py
```

---

## 4. hamnet (VM-based Management)

### Architecture

```
hamnet-mgmt VM (Proxmox)
     ├─ Ansible playbooks
     ├─ Shell scripts
     ├─ Security audit automation (cron @ 2 AM UTC)
     └─ Git repo (/opt/hamnet)
```

### Deployment

**Already deployed** - hamnet runs on dedicated VM in homelab.

**Access**:
```bash
ssh rham-admin@hamnet-mgmt.local
cd /opt/hamnet
```

**No changes needed** - hamnet is self-contained.

---

## 5. hosting-ops (VPS)

### Architecture

```
Heart Internet VPS
     ├─ Python scripts (webhost365 automation)
     ├─ Cron jobs (customer site checks)
     └─ Git repo (/opt/hosting-ops)
```

### Deployment

**TBD** - hosting-ops deployment not yet specified.

**Recommendation**: Deploy similar to ai-cost-tracker (Docker or systemd service).

---

## 6. zebra-ecosystem (Python Library)

### Installation

#### Development (Editable)

```bash
# Clone
cd ~/projects
git clone https://github.com/zebadee2kk/zebra-ecosystem.git

# Install editable
cd zebra-ecosystem
pip install -e .

# Verify
python -c "from zebra_core.models import ModelRegistry; print('✓ Installed')"
```

#### Production (Git Install)

**File**: `requirements.txt` (in control-tower)

```txt
git+https://github.com/zebadee2kk/zebra-ecosystem.git@main
```

```bash
pip install -r requirements.txt
```

### Updates

```bash
# Editable install
cd ~/projects/zebra-ecosystem
git pull

# Git install
pip install --upgrade git+https://github.com/zebadee2kk/zebra-ecosystem.git@main
```

---

## Infrastructure Requirements

### Homelab (Recommended for Phase 3A)

**Minimum**:
- **CPU**: 4 cores (2 for ai-cost-tracker, 2 for portfolio-management)
- **RAM**: 4 GB (2 GB per service)
- **Disk**: 20 GB (10 GB for PostgreSQL, 10 GB for cache)
- **Network**: Static IP on VLAN 10 (Trusted)

**Existing hamnet infrastructure** can handle this.

### VPS (For Phase 3B Production)

**Recommended Specs**:
- **Provider**: DigitalOcean, Linode, or Heart Internet
- **Tier**: $12-20/month
- **CPU**: 2 vCPUs
- **RAM**: 2-4 GB
- **Disk**: 50 GB SSD
- **Bandwidth**: 2 TB/month

**Services to Deploy**:
- ai-cost-tracker (Docker)
- portfolio-management MCP server (Docker or systemd)
- Nginx reverse proxy

---

## Monitoring & Alerts

### GitHub Actions

```yaml
# In workflow
- name: Notify on failure
  if: failure()
  uses: actions/github-script@v6
  with:
    script: |
      github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title: '⚠️ Nightly Decision Desk Failed',
        body: `Workflow run ${context.runId} failed. Check logs.`,
        labels: ['bug', 'automation']
      })
```

### Docker Services

```bash
# Install monitoring stack (optional)
cd /opt/services
git clone https://github.com/stefanprodan/dockprom.git
cd dockprom
docker-compose up -d

# Access Grafana: http://localhost:3001
# Default: admin/admin
```

### Health Checks

**File**: `/opt/services/health-check.sh`

```bash
#!/bin/bash

# Check ai-cost-tracker
if ! curl -sf http://localhost:5000/api/health > /dev/null; then
    echo "⚠️ ai-cost-tracker is DOWN" | mail -s "Service Alert" you@example.com
fi

# Check portfolio-management MCP server
if ! pgrep -f "scanner_server.py" > /dev/null; then
    echo "⚠️ portfolio-management MCP server is DOWN" | mail -s "Service Alert" you@example.com
fi
```

```bash
# Add to cron
crontab -e
# Add: */5 * * * * /opt/services/health-check.sh
```

---

## Backup Strategy

### Git Repos

**Already backed up** - all code in GitHub.

### Databases

**ai-cost-tracker PostgreSQL**:

```bash
# Automated daily backup
crontab -e
# Add:
0 2 * * * docker exec ai-cost-tracker_postgres_1 pg_dump -U ai_cost_tracker ai_cost_tracker | gzip > /backup/ai-cost-tracker-$(date +\%Y\%m\%d).sql.gz

# Keep last 30 days
0 3 * * * find /backup -name "ai-cost-tracker-*.sql.gz" -mtime +30 -delete
```

### Artifacts

**GitHub Actions artifacts** retained for 30 days automatically.

---

## Disaster Recovery

### control-tower

**Recovery Time**: < 5 minutes  
**Procedure**:
1. Re-run failed workflow manually
2. No data loss (stateless)

### ai-cost-tracker

**Recovery Time**: < 30 minutes  
**Procedure**:
1. Restore PostgreSQL from latest backup
2. `docker-compose up -d`

**Data Loss**: Max 24 hours (daily backups)

### portfolio-management

**Recovery Time**: < 10 minutes  
**Procedure**:
1. Restart MCP server
2. Re-scan portfolio (6 hours cached data acceptable loss)

---

## Security Considerations

### Secrets Management

**GitHub Secrets**: Used for GitHub Actions  
**Docker Secrets**: Use `.env` files (not committed to Git)  
**MCP Server**: Environment variables in `claude_desktop_config.json`

### Network Security

**Firewall Rules** (hamnet):
```bash
# Allow internal access to services
sudo ufw allow from 192.168.10.0/24 to any port 5000 comment "ai-cost-tracker"
sudo ufw allow from 192.168.10.0/24 to any port 3000 comment "ai-cost-tracker-dashboard"

# Deny external access
sudo ufw deny 5000
sudo ufw deny 3000
```

### API Security

**ai-cost-tracker**:
- Bearer token authentication
- CORS restrictions
- Rate limiting (100 req/min per IP)

---

## Troubleshooting

### control-tower Workflow Fails

```bash
# Check logs
gh run view <run-id>

# Re-run
gh run rerun <run-id>

# Test locally
act -j decision-desk --secret-file .env.local
```

### ai-cost-tracker Connection Refused

```bash
# Check if service is running
docker ps | grep ai-cost-tracker

# Check logs
docker-compose logs -f api

# Restart
docker-compose restart api
```

### portfolio-management MCP Server Not Responding

```bash
# Check if process is running
ps aux | grep scanner_server.py

# Test manually
python mcp_servers/scanner_server.py

# Check GitHub token
echo $GITHUB_TOKEN | wc -c  # Should be 40+ characters
```

---

## References

- [Ecosystem Architecture](./ECOSYSTEM_ARCHITECTURE.md) - System overview
- [Integration Patterns](./INTEGRATION_PATTERNS.md) - Code examples
- [Phase 3 Roadmap](./PHASE_3_ROADMAP.md) - Implementation timeline
- [hamnet Inventory](https://github.com/zebadee2kk/hamnet/blob/main/inventory/HAMNET-INVENTORY.md) - Infrastructure details

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-28  
**Next Review**: Phase 3A completion
