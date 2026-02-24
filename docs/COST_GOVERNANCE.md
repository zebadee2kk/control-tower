# Cost Governance

## Philosophy

**Structure prevents waste. Gates prevent runaway costs.**

Every piece of work has a cost - whether time, tokens, or £. This system tracks and controls spending before it happens.

## Budget Types

Every issue must declare its budget cap using one or more of:

### Time Budget
- Measured in hours or days
- Example: "2 hours research, 4 hours implementation"

### Token Budget
- For AI model usage
- Example: "100K tokens for code generation"

### Financial Budget
- Direct costs in £
- Example: "£5 for API calls, £0 for local models"

## Budget Declaration

In every issue, specify:

```yaml
Budget Cap:
  Time: X hours
  Tokens: Y tokens
  Cost: £Z

Spend-to-Date:
  Time: 0h
  Tokens: 0
  Cost: £0
```

## Stop-Loss Rules

### Automatic Triggers

When budget cap is reached:
1. Work stops immediately
2. Issue labeled `gate:needs-approval`
3. Added to Decision Desk
4. Requires explicit approval to continue

### Budget Increase Process

1. Comment on issue with justification
2. Propose new cap
3. Wait for approval
4. Update budget fields
5. Resume work

## Model Tier Strategy

### Local Models (Ollama)

**Use for:**
- Summarization
- Classification
- Routine briefings
- Template generation
- Low-risk tasks

**Cost:** Time only (local compute)

### Cloud Models (Premium)

**Use for:**
- Complex planning
- Architecture decisions
- Production code generation
- Financial analysis
- High-stakes outputs

**Cost:** £ per token

### Escalation Rules

1. **Always try local first**
2. Escalate to cloud if quality insufficient
3. Require approval for premium model use
4. Document why escalation needed

## Cost Tracking

### Per Issue

Update issue description or add comment:

```markdown
## Cost Update - YYYY-MM-DD

- Time spent: +2h (total: 4h / 6h cap)
- Tokens used: +15K (total: 35K / 100K cap)
- Cost: +£1.20 (total: £2.50 / £5 cap)

Status: ON TRACK / APPROACHING CAP / CAP EXCEEDED
```

### Portfolio Level

Weekly, update ecosystem map with:
- Total time invested per repo
- Total costs per project
- ROI assessment

## Premium Usage Gates

Requires explicit approval for:

- GPT-4 or equivalent (> £0.01/1K tokens)
- Long context windows (> 32K tokens)
- Multiple retries (> 3 attempts)
- Financial modeling or projections
- Production code deployment

## Budget Templates

### Small Research Task
```yaml
Time: 1-2 hours
Tokens: 50K (local models)
Cost: £0
```

### Medium Planning Task
```yaml
Time: 3-4 hours
Tokens: 100K (mix of local + cloud)
Cost: £2-3
```

### Large Implementation Task
```yaml
Time: 1-2 days
Tokens: 200K (cloud heavy)
Cost: £10-15
```

## Cost Review Triggers

### Immediate Review Required

- Any single task > £20
- Monthly total > £100
- 3+ budget cap breaches
- Unexpected cost spike

### Weekly Review

- Portfolio cost summary
- Cost per outcome delivered
- Model efficiency assessment
- Identify waste patterns

## Waste Prevention

### Common Cost Sinks

❌ Research loops without decision deadlines  
❌ Premium models for simple tasks  
❌ Re-generating same content multiple times  
❌ Unstructured exploration without clear goals  
❌ Over-engineering before validation  

### Cost Discipline

✅ Clear acceptance criteria before starting  
✅ Local models as default  
✅ Time-boxed research phases  
✅ Reuse existing outputs  
✅ Batch similar tasks  

## Emergency Stops

If costs are running away:

1. **STOP ALL WORK**
2. Label all active issues `gate:paused`
3. Create emergency Decision Desk
4. Root cause analysis
5. Revise cost governance if needed
6. Resume only after approval

---

**Remember:** The goal is controlled progress, not zero cost. Invest strategically, cut waste ruthlessly.