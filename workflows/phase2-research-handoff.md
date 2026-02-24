# Phase 2 Research Handoff Package

**For:** Issue #13 - Phase 2 Automation Pilot  
**Phase:** Research (Days 1-2)  
**Assigned to:** Perplexity (Research) → VS Code (Implementation)  
**Timeline:** Feb 25-26, 2026  
**Budget:** 3 hours, £0

---

## Context

We're building GitHub Actions workflows to automate the Control Tower. This requires understanding:
- How GitHub Actions handles issue automation
- Label-driven workflow patterns
- Scheduled jobs (nightly Decision Desk)
- Human-in-the-loop approval gates
- IssueOps best practices

---

## Research Questions

### Q1: Label-Driven Issue Automation

**What we need to know:**
- How to trigger workflows when labels are added/removed
- Best practices for label-based state management
- How to automatically close issues with specific labels
- How to add labels when issues are closed
- Handling label changes to move issues between states

**Key patterns to find:**
- Workflow triggers: `on.issues.labeled`
- GitHub Script action for label manipulation
- Label validation and enforcement

**Sources researched:** [web:100][web:101][web:104][web:107][web:110]

**Key Findings:**

**IssueOps Pattern** [web:100][web:120][web:122][web:125]:
- GitHub + IssueOps = full automation via issues and Actions
- Use `issue_comment` trigger for command-based workflows
- `actions/github-script` provides authenticated GitHub API access
- Labels can drive state machines via workflow triggers

**Label-Based Workflows** [web:104][web:107][web:110]:
- Trigger: `on.issues.labeled` or `on.pull_request.labeled`
- Use `if: contains(github.event.label.name, 'pattern')` for filtering
- `actions/github-script` can create/update/delete labels programmatically
- Best practice: One workflow file per automation concern

**Automation Examples** [web:101][web:103][web:119]:
- Auto-comment on new issues
- Auto-close stale issues
- Auto-assign based on labels
- Label-to-project-column mapping

---

### Q2: Scheduled Workflows (Nightly Decision Desk)

**What we need to know:**
- How to schedule workflows with cron syntax
- Timezone handling (we need 9 PM GMT)
- How to create issues from workflows
- How to query existing issues and aggregate data
- How to close previous issues automatically

**Key patterns to find:**
- `schedule` trigger with cron
- Creating issues via API
- Querying issues with labels
- UTC time conversion

**Sources researched:** [web:105][web:106][web:108][web:111]

**Key Findings:**

**Scheduled Jobs** [web:105][web:108][web:111]:
- Use `on.schedule.cron: '0 21 * * *'` for 9 PM UTC (= 9 PM GMT)
- Minimum interval: every 5 minutes (`*/5 * * * *`)
- **Critical**: All schedules run in UTC
- **Best practice**: Avoid scheduling on the hour (high load)
- Schedules only run on default branch

**Cron Syntax**:
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6)
│ │ │ │ │
0 21 * * * = Every day at 9 PM UTC
```

**Issue Creation** [web:119][web:120]:
- Use `actions/github-script` with `github.rest.issues.create()`
- Can include templated body with aggregated data
- Can assign to users and add labels

---

### Q3: Human-in-the-Loop Approval Gates

**What we need to know:**
- How to pause workflows for manual approval
- Approval via issue comments
- Environment-based approvals (if free tier supports)
- How to enforce gate:needs-approval label

**Key patterns to find:**
- Manual approval actions
- Issue comment parsing for approval
- Workflow blocking mechanisms

**Sources researched:** [web:114][web:115][web:116][web:117][web:118][web:121][web:123]

**Key Findings:**

**Manual Approval Action** [web:118]:
- `trstringer/manual-approval` action available
- Creates approval issue automatically
- Waits for approver comments with keywords
- **Free for private repos** (doesn't require GitHub Enterprise)
- Pattern: Workflow → Creates issue → Waits → Continues on approval

**Human-in-the-Loop Patterns** [web:114][web:115][web:117][web:123]:
- Create approval request as issue/comment
- Agent/workflow polls for approval response
- Continue/abort based on human decision
- Log approval decision for audit trail

**Our Approach for Control Tower**:
- Don't block workflows - we're not doing CD/deployment
- Instead: `gate:needs-approval` label triggers creation of Decision Desk item
- Human reviews in nightly Decision Desk
- Human manually removes gate or changes state
- Simple, auditable, non-blocking

---

### Q4: GitHub Actions Best Practices

**What we need to know:**
- Security considerations
- Performance optimization
- Error handling
- Workflow organization

**Sources researched:** [web:99][web:102][web:103][web:112][web:113]

**Key Findings:**

**Security** [web:102]:
- Never commit secrets or tokens
- Use `GITHUB_TOKEN` (auto-provided)
- Limit permissions with `permissions:` key
- Validate inputs from issue bodies

**Performance** [web:103][web:112]:
- Keep workflows focused and single-purpose
- Avoid scheduling exactly on the hour
- Use caching where appropriate
- Minimize API calls

**Organization** [web:102][web:112]:
- One workflow file per automation
- Use clear names: `label-automation.yml`, `nightly-decision-desk.yml`
- Document workflow purpose in comments
- Use reusable workflows for common patterns

**Syntax** [web:113]:
- `on:` defines triggers
- `jobs:` defines work to do
- `steps:` defines sequential actions
- `if:` for conditional execution

---

## Recommendations

### Workflow 1: Label-Based State Management

**File:** `.github/workflows/label-automation.yml`

**Triggers:**
- `on.issues.labeled`
- `on.issues.unlabeled`
- `on.issues.closed`

**Logic:**
```yaml
- If issue labeled 'state:done' → close issue
- If issue closed → add 'state:done' if missing
- If issue labeled 'gate:needs-approval' → add comment "Added to Decision Desk"
```

**Implementation:** Use `actions/github-script`

---

### Workflow 2: Nightly Decision Desk

**File:** `.github/workflows/nightly-decision-desk.yml`

**Trigger:**
```yaml
on:
  schedule:
    - cron: '0 21 * * *'  # 9 PM UTC = 9 PM GMT
  workflow_dispatch:  # Allow manual trigger for testing
```

**Logic:**
1. Query all issues with `gate:needs-approval`
2. Query all issues with `state:blocked`
3. Create new Decision Desk issue with:
   - Date in title
   - List of approval-needed issues
   - List of blocked issues
   - Labels: `state:awaiting-decision`, `gate:needs-approval`, `p0`
4. Close previous Decision Desk issue (if exists)

**Implementation:** Use `actions/github-script` + GitHub GraphQL/REST API

---

### Workflow 3: WIP Limit Enforcement

**File:** `.github/workflows/wip-limit-check.yml`

**Triggers:**
- `on.issues.labeled` (when state changes)

**Logic:**
```yaml
- Count issues with 'state:build'
- Count issues with 'state:research'
- If either > 3:
  - Add comment to issue: "WIP limit reached. Current: X. Max: 3."
  - Add 'state:blocked' label
  - Remove the state label that would exceed limit
```

---

### Workflow 4: Weekly Cost Rollup

**File:** `.github/workflows/weekly-cost-rollup.yml`

**Trigger:**
```yaml
on:
  schedule:
    - cron: '0 18 * * 0'  # 6 PM UTC every Sunday
  workflow_dispatch:
```

**Logic:**
1. Query all issues updated in past 7 days
2. Parse budget comments (format: `Budget: Xh, £Y`)
3. Aggregate totals
4. Create weekly report issue
5. Flag budget overruns

---

## Architecture Decision

**Approach:** IssueOps + Label-Driven State Machine

**Why:**
- Simple and auditable
- No external dependencies
- Free tier compatible
- Human-in-the-loop by design
- Uses GitHub native features only

**Not using:**
- Environment-based approvals (requires Enterprise for private repos)
- Blocking approval workflows (we're not doing deployments)
- External orchestration tools
- Complex state machines

---

## Risks & Mitigations

**Risk 1:** Workflow bugs break issue management
- **Mitigation:** Test on non-critical issues first, use `workflow_dispatch` for manual testing

**Risk 2:** Scheduled jobs don't run (GitHub Actions load)
- **Mitigation:** Schedule at off-peak times (9 PM is good), add `workflow_dispatch` for manual trigger

**Risk 3:** Over-automation removes human oversight
- **Mitigation:** Keep gates manual, only automate state transitions and notifications

---

## Next Steps (Implementation Phase)

1. Create `.github/workflows/label-automation.yml`
2. Create `.github/workflows/nightly-decision-desk.yml`
3. Test workflows with `workflow_dispatch` triggers
4. Iterate based on real usage
5. Document in `docs/AUTOMATION_GUIDE.md`
6. Extract gold vault lessons learned

---

## Handoff to VS Code

This research provides the blueprint. VS Code/Copilot will:
1. Read this file
2. Generate workflow YAML files
3. Test locally (syntax validation)
4. Commit and push
5. Test via `workflow_dispatch`
6. Document results

**Estimated implementation time:** 4-6 hours over Days 3-5

---

## Sources Referenced

- GitHub Actions Documentation [web:99][web:113]
- IssueOps Patterns [web:100][web:120][web:125]
- Label Automation [web:104][web:107][web:110]
- Scheduled Workflows [web:105][web:108][web:111]
- Manual Approval [web:118][web:121]
- Best Practices [web:102][web:112]

**Research complete.** Ready for implementation phase.
