# ai-cost-tracker Quick Start Checklist

**Date:** 2026-03-01  
**Purpose:** Fast-track local deployment with VSCode Copilot  
**Time:** 60-90 minutes  
**Prerequisites:** Docker, VSCode, Git

---

## 🚀 10-Step Deployment

### ☑️ Step 1: Clone (2 min)

```bash
cd ~/projects
git clone https://github.com/zebadee2kk/ai-cost-tracker.git
cd ai-cost-tracker
code .
```

### ☑️ Step 2: Generate Secrets (2 min)

```bash
# Run these two commands and save the output:
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
```

### ☑️ Step 3: Create .env (5 min)

```bash
cp .env.example .env
```

Edit `.env` with:
- ENCRYPTION_KEY from Step 2
- SECRET_KEY from Step 2
- DATABASE_URL=postgresql://postgres:postgres@db:5432/ai_cost_tracker
- REACT_APP_API_URL=http://localhost:5000

### ☑️ Step 4: Start Services (5 min)

```bash
docker-compose up -d
docker-compose logs -f  # Watch startup (Ctrl+C when done)
```

Wait for:
- "database system is ready"
- "Running on http://0.0.0.0:5000"
- "webpack compiled successfully"

### ☑️ Step 5: Initialize Database (3 min)

```bash
docker-compose exec backend flask db upgrade
docker-compose exec backend python scripts/seed_services.py
```

### ☑️ Step 6: Health Check (2 min)

```bash
curl http://localhost:5000/api/health
```

Expected: `{"status":"healthy","database":"connected"}`

Open: http://localhost:3000 (should see login page)

### ☑️ Step 7: Create User (2 min)

In browser:
1. Go to http://localhost:3000
2. Click **Sign Up**
3. Email: `test@example.com`, Password: `SecurePass123!`
4. Click **Register**

### ☑️ Step 8: Add AI Account (3 min)

1. Dashboard → **Add Account**
2. Select **Groq** (no API key needed for testing)
3. Set limit: `100`
4. Click **Save**

### ☑️ Step 9: Test Manual Entry (3 min)

1. Select your Groq account
2. Click **Add Manual Entry**
3. Date: Today, Cost: `15.50`, Tokens: `1000000`
4. Click **Save**

Should see entry in dashboard!

### ☑️ Step 10: Test Export (2 min)

1. Dashboard → **History** tab
2. Click **Export** → **CSV**
3. Click **Download**

File should download with your data!

---

## ✅ Success Criteria

- [ ] Frontend loads at http://localhost:3000
- [ ] Backend API responds at http://localhost:5000/api/health
- [ ] User can log in
- [ ] Account added successfully
- [ ] Manual entry persists
- [ ] CSV export downloads
- [ ] No errors in `docker-compose logs`

---

## 🐛 Quick Troubleshooting

**Port in use?**
```bash
lsof -ti:5000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

**Database issues?**
```bash
docker-compose restart db
docker-compose logs db
```

**Need to reset?**
```bash
docker-compose down -v  # WARNING: Deletes all data
docker-compose up -d
# Repeat Steps 5-10
```

---

## 📚 Full Documentation

See [HANDOFF_2026-03-01_AI_COST_TRACKER_DEPLOYMENT.md](HANDOFF_2026-03-01_AI_COST_TRACKER_DEPLOYMENT.md) for:
- Detailed explanations
- Architecture diagrams
- Common issues & solutions
- VSCode Copilot tips
- Phase 3A integration preview

---

## 🚀 Ready for Phase 3A!

Once all 10 steps complete, you're ready to integrate with control-tower.

**Next:** Open VSCode, use GitHub Copilot Chat, and reference the full handoff document for any questions.

**Estimated Time:** 30 minutes with no issues, 60-90 minutes if troubleshooting needed.

**Good luck!** 🎉
