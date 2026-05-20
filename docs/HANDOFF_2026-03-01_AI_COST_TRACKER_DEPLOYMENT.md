# VSCode Copilot Handoff: ai-cost-tracker Local Deployment

**Date:** 2026-03-01  
**Purpose:** Guide VSCode Copilot through local deployment of ai-cost-tracker for Phase 3A integration testing  
**Owner:** Richard Ham (@zebadee2kk)  
**Target Environment:** Local development (macOS/Linux/Windows)  
**Expected Duration:** 1-2 hours

---

## 🎯 Objective

Deploy ai-cost-tracker locally in VSCode with Docker Compose, verify all components are working, and prepare for control-tower integration in Phase 3A Week 1.

---

## 📋 Context for Copilot

### What is ai-cost-tracker?

A unified dashboard tracking AI service usage and costs across:
- OpenAI/ChatGPT (automatic API sync)
- Anthropic Claude (automatic API sync)
- Groq (manual entry)
- Perplexity (manual entry)

**Tech Stack:**
- **Backend**: Flask, SQLAlchemy, PostgreSQL, APScheduler
- **Frontend**: React 18, Chart.js, Axios
- **Deployment**: Docker Compose with 3 services (backend, frontend, database)

**Current Status:**
- Phase 3 Sprint 2 COMPLETE (Feb 27, 2026)
- Full notification system operational
- 121+ passing tests
- CI/CD pipeline active
- Production-ready codebase

### Why Deploy Locally?

1. **Phase 3A Integration Testing**: control-tower will integrate with ai-cost-tracker API
2. **Development Environment**: Test control-tower's cost tracking features locally
3. **Pre-Production Validation**: Verify deployment before homelab/VPS production deployment
4. **Learning**: Understand the codebase and architecture hands-on

---

## 🚀 Deployment Steps

### Step 1: Clone Repository (5 minutes)

```bash
# Navigate to projects directory
cd ~/projects  # or your preferred location

# Clone ai-cost-tracker
git clone https://github.com/zebadee2kk/ai-cost-tracker.git
cd ai-cost-tracker

# Open in VSCode
code .
```

**Verification:**
- ✅ VSCode opens with ai-cost-tracker workspace
- ✅ You see backend/, frontend/, docs/, docker-compose.yml
- ✅ README.md displays Phase 3 Sprint 2 Complete status

---

### Step 2: Environment Configuration (10 minutes)

**Task for Copilot:** Generate required secrets and configure .env file

```bash
# Generate encryption key
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"

# Generate Flask secret key
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
```

**Create .env file:**

```bash
# Copy example
cp .env.example .env
```

**Edit .env with these values:**

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=<generated-from-step-above>

# Database
DB_CONNECTION_STRING=<database-connection-string-from-secret-store>

# Encryption
ENCRYPTION_KEY=<generated-from-step-above>

# JWT
JWT_SECRET_KEY=<same-as-SECRET_KEY-or-generate-new>

# Frontend
REACT_APP_API_URL=http://localhost:5000

# Optional: Notifications (can be added later)
# SENDGRID_API_KEY=your-sendgrid-key
# SENDGRID_FROM_EMAIL=alerts@example.com
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Rate Limiting (defaults are fine for local dev)
EMAIL_RATE_LIMIT_HOURLY=10
EMAIL_RATE_LIMIT_DAILY=50
SLACK_RATE_LIMIT_HOURLY=20
SLACK_RATE_LIMIT_DAILY=100
```

**Important Notes:**
- ⚠️ Keep .env file private (it's in .gitignore)
- ✅ Notification services (SendGrid, Slack) are OPTIONAL for local testing
- ✅ You can add API keys later if you want to test notifications

**Verification:**
- ✅ .env file exists with all required variables
- ✅ ENCRYPTION_KEY and SECRET_KEY are set
- ✅ DATABASE_URL points to Docker Compose database

---

### Step 3: Docker Compose Deployment (15 minutes)

**Prerequisites Check:**
```bash
# Verify Docker is running
docker --version
docker-compose --version

# Expected output:
# Docker version 24.x.x or higher
# docker-compose version 2.x.x or higher
```

**Start Services:**

```bash
# Build and start all containers (backend, frontend, database)
docker-compose up -d

# Watch logs to see startup progress
docker-compose logs -f

# Expected output:
# db_1       | database system is ready to accept connections
# backend_1  | * Running on http://0.0.0.0:5000
# frontend_1 | webpack compiled successfully
```

**Wait for all services to be healthy** (usually 30-60 seconds)

Press Ctrl+C to stop watching logs (containers continue running in background)

**Verification:**
- ✅ Three containers running: ai-cost-tracker_backend, ai-cost-tracker_frontend, ai-cost-tracker_db
- ✅ No error messages in logs
- ✅ Backend shows "Running on http://0.0.0.0:5000"
- ✅ Frontend shows "webpack compiled successfully"

---

### Step 4: Database Initialization (5 minutes)

**Apply Migrations:**

```bash
# Run database migrations (creates all tables including Phase 3 notification tables)
docker-compose exec backend flask db upgrade

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade -> xxxxx, Phase 1 tables
# INFO  [alembic.runtime.migration] Running upgrade xxxxx -> yyyyy, Phase 2 tables
# INFO  [alembic.runtime.migration] Running upgrade yyyyy -> zzzzz, Phase 3 notification tables
```

**Seed Initial Data:**

```bash
# Populate services table (OpenAI, Anthropic, Groq, Perplexity)
docker-compose exec backend python scripts/seed_services.py

# Expected output:
# Seeding services...
# ✓ ChatGPT added
# ✓ Anthropic added
# ✓ Groq added
# ✓ Perplexity added
# Seeding complete: 4 services created
```

**Verification:**
- ✅ Migrations complete with no errors
- ✅ 4 AI services seeded successfully

---

### Step 5: Health Checks (10 minutes)

**Backend API Health:**

```bash
# Test backend health endpoint
curl http://localhost:5000/api/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "version": "3.2.0"
}
```

**Frontend Access:**

Open browser: http://localhost:3000

**Expected:**
- ✅ Login page displays
- ✅ No console errors (check browser DevTools)
- ✅ Page loads without timeouts

**Database Connection:**

```bash
# Check database tables
docker-compose exec db psql -U postgres -d ai_cost_tracker -c "\dt"

# Expected output: List of tables including:
# users, accounts, services, usage_records, alerts
# notification_preferences, notification_queue, notification_history
```

**Verification Checklist:**
- ✅ Backend API responds at :5000
- ✅ Frontend loads at :3000
- ✅ Database has all tables created
- ✅ No error messages in any service logs

---

### Step 6: Create Test User (5 minutes)

**Register First User:**

1. Open http://localhost:3000
2. Click **Sign Up**
3. Enter:
   - Email: `test@example.com`
   - Password: `SecurePass123!`
4. Click **Register**

**Expected:**
- ✅ Registration succeeds
- ✅ Automatic login occurs
- ✅ Redirected to Dashboard

**Or via API (alternative):**

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'

# Expected response:
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "test@example.com"
  }
}
```

**Verification:**
- ✅ User created successfully
- ✅ Can log in with credentials
- ✅ Dashboard displays (empty, no accounts yet)

---

### Step 7: Add Test AI Account (10 minutes)

**Important:** For local testing, you can add accounts WITHOUT real API keys to verify UI flow.

**Option A: Test with Groq (No API Key Required)**

1. Dashboard → **Add Account** button
2. Select **Groq** from dropdown
3. Set monthly limit: `100` (optional)
4. Click **Save**

**Expected:**
- ✅ Account created successfully
- ✅ Groq account appears in dashboard
- ✅ Shows "Manual Entry" badge (no automatic sync)

**Option B: Test with OpenAI (Requires Real API Key)**

Only do this if you want to test automatic sync:

1. Dashboard → **Add Account**
2. Select **ChatGPT**
3. Paste OpenAI API key: `sk-...`
4. Set monthly limit: `100` (optional)
5. Click **Save**

**Expected:**
- ✅ Account created and API key encrypted
- ✅ Usage sync starts automatically (every hour)
- ✅ Recent usage data appears within 5 minutes

**Verification:**
- ✅ At least one AI account configured
- ✅ Account displays in dashboard
- ✅ No errors when adding account

---

### Step 8: Test Manual Entry (5 minutes)

**Add Manual Usage Data:**

1. Dashboard → Select your account (Groq or any)
2. Click **Add Manual Entry** button
3. Enter:
   - Date: Today's date
   - Cost: `15.50`
   - Tokens (optional): `1000000`
4. Click **Save**

**Expected:**
- ✅ Manual entry created
- ✅ Entry appears in usage history
- ✅ Shows "Manual" badge
- ✅ Dashboard totals update

**Verification:**
- ✅ Manual entry workflow works
- ✅ Data persists across page reloads
- ✅ Costs calculate correctly

---

### Step 9: Test Export Functionality (5 minutes)

**Export Usage Data:**

1. Dashboard → **History** tab
2. Click **Export** button
3. Select **CSV** format
4. Click **Download**

**Expected:**
- ✅ CSV file downloads immediately
- ✅ File opens in Excel/Sheets
- ✅ Contains your manual entry data
- ✅ Shows service, account, cost, tokens, source

**Alternative JSON Export:**

Same steps but select **JSON** format

**Verification:**
- ✅ Both CSV and JSON export work
- ✅ Data is formatted correctly
- ✅ No server errors

---

### Step 10: Integration Readiness Check (10 minutes)

**Test API Endpoints:**

```bash
# Get JWT token (use your test user credentials)
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}' \
  | jq -r '.access_token')

# Test accounts endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/accounts

# Test usage endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/usage

# Test services endpoint
curl http://localhost:5000/api/services
```

**Expected:**
- ✅ All endpoints return 200 OK
- ✅ JSON responses are well-formed
- ✅ Authentication works with JWT

**API Documentation:**

Key endpoints control-tower will use in Phase 3A:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | System health check |
| `/api/auth/login` | POST | Get JWT token |
| `/api/accounts` | GET | List user's AI accounts |
| `/api/usage` | GET | Fetch usage data |
| `/api/usage/manual` | POST | Add manual entry |
| `/api/alerts` | GET | Get cost alerts |
| `/api/notifications/preferences` | GET/POST | Notification settings |

**Verification:**
- ✅ All API endpoints accessible
- ✅ Authentication working
- ✅ Data flows correctly
- ✅ Ready for control-tower integration

---

## 🎓 Understanding the Architecture

### Service Architecture

```
┌─────────────────────────────────────────────────────┐
│          Frontend (React) :3000                     │
│  Dashboard · Analytics · Settings · Export         │
└──────────────────┬──────────────────────────────────┘
                   │ Axios HTTP + JWT
                   ↓
┌─────────────────────────────────────────────────────┐
│          Backend API (Flask) :5000                  │
│  /api/auth   /api/accounts   /api/usage            │
│  /api/notifications   /api/alerts                  │
└──────┬──────────────────────────────┬───────────────┘
       │                              │
  PostgreSQL :5432              APScheduler
  (Docker container)            (background jobs)
  - User accounts               - Usage sync (hourly)
  - AI service configs          - Notification sender
  - Usage records               - Alert generator
  - Notification queue
```

### Data Flow for Automatic Sync

1. **Hourly Job** (APScheduler) → `jobs/sync_usage.py`
2. **API Call** → OpenAI/Anthropic billing API
3. **Idempotent Upsert** → PostgreSQL (no duplicates)
4. **Alert Check** → If threshold exceeded, create alert
5. **Notification** → Email/Slack if configured

### Data Flow for Manual Entry

1. **User Input** → Frontend form
2. **POST** → `/api/usage/manual`
3. **Validation** → Backend checks data
4. **Insert** → PostgreSQL with `source='manual'`
5. **Response** → Frontend updates dashboard

---

## 🐛 Common Issues & Solutions

### Issue 1: Port Already in Use

**Symptom:**
```
Error: bind: address already in use
```

**Solution:**
```bash
# Find process using port 5000 or 3000
lsof -ti:5000
lsof -ti:3000

# Kill the process
kill -9 <PID>

# Or change ports in docker-compose.yml:
# "3001:3000" for frontend
# "5001:5000" for backend
```

### Issue 2: Database Connection Failed

**Symptom:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check database container is running
docker-compose ps

# If db is down, restart it
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Issue 3: Migration Fails

**Symptom:**
```
ERROR [alembic.runtime.migration] Can't locate revision
```

**Solution:**
```bash
# Reset database and start fresh
docker-compose down -v  # WARNING: Deletes all data
docker-compose up -d
docker-compose exec backend flask db upgrade
docker-compose exec backend python scripts/seed_services.py
```

### Issue 4: Frontend Not Loading

**Symptom:** Blank page or "Cannot GET /" error

**Solution:**
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend

# Clear browser cache and reload
```

### Issue 5: API Key Encryption Error

**Symptom:**
```
cryptography.fernet.InvalidToken: Token decryption failed
```

**Solution:**
- ENCRYPTION_KEY changed after data was encrypted
- Either restore old key or reset database
- For local dev, safest to `docker-compose down -v` and start fresh

---

## 📊 Success Criteria

After completing all steps, you should have:

- ✅ **3 Docker containers running** (backend, frontend, db)
- ✅ **Frontend accessible** at http://localhost:3000
- ✅ **Backend API responding** at http://localhost:5000
- ✅ **Database initialized** with all tables
- ✅ **Test user created** and can log in
- ✅ **At least one AI account** configured
- ✅ **Manual entry works** (data persists)
- ✅ **Export functionality** works (CSV/JSON)
- ✅ **API endpoints tested** with JWT auth
- ✅ **No error messages** in any logs

**System Status: READY FOR PHASE 3A INTEGRATION** 🎉

---

## 🚀 Next Steps After Deployment

### Immediate (Tonight/Tomorrow Morning)

1. **Document API Endpoints** you'll use from control-tower
2. **Test Notification System** (optional - add SendGrid key)
3. **Explore Dashboard** - familiarize yourself with UI
4. **Check Logs** - understand what scheduled jobs are doing

### Phase 3A Week 1 (Monday - Friday)

**Monday:**
1. Implement Codex's security hardening (control-tower)
2. Design control-tower ↔ ai-cost-tracker integration
3. Create `docs/INTEGRATION_PLAN.md`

**Tuesday-Wednesday:**
4. Build control-tower integration layer
5. Add cost tracking to Decision Desk workflow
6. Test end-to-end cost attribution

**Thursday-Friday:**
7. Weekly Cost Rollup integration
8. Dashboard enhancements
9. Documentation updates

---

## 📚 Resources for Copilot

### Key Files to Review

**Backend:**
- `backend/app.py` - Flask app initialization
- `backend/routes/` - All API endpoints
- `backend/models/` - Database schemas
- `backend/jobs/sync_usage.py` - Automatic sync logic
- `backend/services/notifications/` - Email/Slack senders

**Frontend:**
- `frontend/src/pages/Dashboard.jsx` - Main dashboard
- `frontend/src/services/api.js` - HTTP client
- `frontend/src/components/` - Reusable components

**Configuration:**
- `docker-compose.yml` - Container orchestration
- `.env.example` - Configuration template
- `backend/migrations/` - Database schema history

### Documentation

- `README.md` - Complete project documentation
- `docs/phase3-status.md` - Current sprint status
- `docs/phase3-roadmap.md` - Feature specifications
- `docs/setup-quickstart.md` - Detailed setup guide
- `docs/phase3-notifications-spec.md` - Notification system design

### Testing

```bash
# Run backend tests
docker-compose exec backend pytest tests/ -v

# Run with coverage
docker-compose exec backend pytest tests/ --cov=. --cov-report=html

# View coverage report
open backend/htmlcov/index.html
```

---

## 💡 Tips for VSCode Copilot

### When Asking Copilot for Help:

**Good Prompts:**
- "Explain how the idempotent upsert works in sync_usage.py"
- "Show me how to add a new API endpoint for cost forecasting"
- "Help me understand the notification rate limiting logic"
- "What's the data flow when a manual entry is created?"

**Include Context:**
- "I'm working in ai-cost-tracker's backend/routes/usage.py"
- "Looking at the UsageRecord model - how are timestamps normalized?"
- "Frontend Dashboard.jsx - where does the chart data come from?"

**For Debugging:**
- Share error messages with file paths
- Include relevant log output
- Mention what you've already tried

### VSCode Extensions to Install:

- **Python** (Microsoft) - IntelliSense and debugging
- **Pylance** - Fast Python type checking
- **Docker** (Microsoft) - Manage containers in VSCode
- **SQLTools** - Database explorer for PostgreSQL
- **ES7+ React/Redux/React-Native snippets** - Frontend development
- **REST Client** - Test API endpoints directly in VSCode

---

## 🎯 Phase 3A Integration Preview

Once ai-cost-tracker is deployed, control-tower will:

1. **Cost Attribution**: Track which GitHub workflows triggered which AI API calls
2. **Budget Enforcement**: Decision Desk considers costs before approving work
3. **Automated Reporting**: Weekly Cost Rollup pulls data from ai-cost-tracker API
4. **Alert Routing**: ai-cost-tracker alerts flow into control-tower's Decision Desk
5. **Unified Dashboard**: Single pane of glass for project health + AI costs

**Integration Pattern:**

```python
# control-tower workflow will call ai-cost-tracker API
import requests

# Get current month's costs
response = requests.get(
    "http://localhost:5000/api/usage",
    headers={"Authorization": f"Bearer {jwt_token}"},
    params={"start_date": "2026-03-01", "end_date": "2026-03-31"}
)

costs = response.json()
total_cost = sum(record["cost"] for record in costs)

# Decision logic
if total_cost > budget_threshold:
    create_decision_desk_issue("Budget exceeded - review needed")
```

---

## ✅ Deployment Checklist

Use this checklist to track your progress:

- [ ] Repository cloned and opened in VSCode
- [ ] .env file created with all required secrets
- [ ] Docker Compose services started successfully
- [ ] Database migrations applied
- [ ] Initial services seeded (4 AI services)
- [ ] Backend health check passes
- [ ] Frontend loads without errors
- [ ] Test user registered and logged in
- [ ] At least one AI account added
- [ ] Manual entry created and visible
- [ ] CSV export downloads successfully
- [ ] API endpoints tested with curl/Postman
- [ ] All containers running with no errors
- [ ] Ready for Phase 3A integration work

---

## 📞 Support

**If you encounter issues:**

1. **Check logs first:**
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   docker-compose logs db
   ```

2. **Review documentation:**
   - README.md sections relevant to your issue
   - docs/setup-quickstart.md for detailed setup steps

3. **Ask Copilot with context:**
   - Share error messages
   - Mention what step you're on
   - Include relevant file paths

4. **GitHub Issues:**
   - Check existing issues: https://github.com/zebadee2kk/ai-cost-tracker/issues
   - Create new issue if needed (include logs and .env structure - NO SECRETS)

---

## 🎉 You're Ready!

When you see:
- ✅ http://localhost:3000 shows the dashboard
- ✅ http://localhost:5000/api/health returns healthy
- ✅ No errors in `docker-compose logs`

**Congratulations!** 🎊 

You've successfully deployed ai-cost-tracker locally and are ready to start Phase 3A integration work with control-tower.

**Estimated Total Time:** 60-90 minutes  
**Complexity:** Medium (Docker Compose + multi-service architecture)  
**Prerequisites:** Docker, VSCode, basic command line familiarity

---

**Good luck with the deployment! VSCode Copilot is here to help every step of the way.** 🚀

**Last Updated:** 2026-03-01  
**Version:** 1.0  
**Status:** Ready for deployment
