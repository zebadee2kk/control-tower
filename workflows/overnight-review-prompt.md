# Overnight Review Prompt for GitHub Copilot

**Date:** 2026-02-24  
**Purpose:** Review Phase 2 automation workflows for bugs, security issues, and improvements  
**Timeline:** Overnight review, report ready by morning  

---

## Instructions for Copilot

You are reviewing the Control Tower Phase 2 automation implementation. Perform a comprehensive audit of all 4 GitHub Actions workflows and the overall system.

---

## Review Checklist

### 1. Workflow Syntax & Correctness

**For each workflow file in `.github/workflows/`:**

- [ ] YAML syntax is valid (no indentation errors)
- [ ] All required fields present (`name`, `on`, `jobs`, `steps`)
- [ ] Triggers are correctly defined
- [ ] Job names and step names are descriptive
- [ ] `permissions:` block is present and minimal
- [ ] `if:` conditionals use correct syntax

**Check:**
```bash
cd .github/workflows
for file in *.yml; do
  echo "Checking $file..."
  yamllint $file 2>&1 || echo "Note: yamllint not required, manual review OK"
done
```

**Document any issues in:** `docs/WORKFLOW_REVIEW.md`

---

### 2. Security Review

**Check for:**

- [ ] No hardcoded secrets or tokens
- [ ] Uses `GITHUB_TOKEN` (auto-provided)
- [ ] `permissions:` scoped to minimum required:
  - `issues: write` for issue operations
  - `contents: read` for reading repo
- [ ] No user input directly interpolated without sanitization
- [ ] No `eval` or dangerous script execution
- [ ] All external actions pinned to specific versions or trusted sources

**Review actions used:**
- `actions/github-script@v7` - Official GitHub action ✅
- Any others? Document in review.

**Document findings in:** `docs/SECURITY_REVIEW.md`

---

### 3. Logic & Correctness

**Label Automation (`label-automation.yml`):**

- [ ] Correctly closes issues with `state:done` label
- [ ] Adds `state:done` to closed issues if missing
- [ ] Comments on `gate:needs-approval` label
- [ ] Doesn't create infinite loops (e.g., adding label triggers itself)
- [ ] Handles edge cases (label already present, issue already closed)

**Nightly Decision Desk (`nightly-decision-desk.yml`):**

- [ ] Cron schedule is correct: `0 21 * * *` = 9 PM UTC
- [ ] Queries issues with correct labels
- [ ] Creates properly formatted Decision Desk issue
- [ ] Closes previous Decision Desk (if exists)
- [ ] Handles case when no issues need decisions
- [ ] `workflow_dispatch` present for manual testing

**WIP Limit Check (`wip-limit-check.yml`):**

- [ ] Correctly counts issues in `state:build` and `state:research`
- [ ] Checks limit (3 per state)
- [ ] Adds blocking comment when limit exceeded
- [ ] Doesn't accidentally block all issues
- [ ] Only triggers on relevant label changes

**Weekly Cost Rollup (`weekly-cost-rollup.yml`):**

- [ ] Cron schedule: `0 18 * * 0` = 6 PM UTC on Sundays
- [ ] Queries issues from past 7 days
- [ ] Parses budget comments correctly
- [ ] Aggregates totals accurately
- [ ] Creates formatted report issue
- [ ] Handles missing budget data gracefully

**Test each workflow logic by tracing through the code mentally or with sample data.**

**Document findings in:** `docs/LOGIC_REVIEW.md`

---

### 4. Performance & Efficiency

**Check for:**

- [ ] Minimal API calls (batch where possible)
- [ ] No unnecessary loops
- [ ] Efficient GraphQL queries (if used)
- [ ] Reasonable timeout limits
- [ ] Caching where appropriate

**API Rate Limits:**
- GitHub Actions has 1,000 API requests per hour per repository
- Each workflow should use < 50 calls per run

**Document findings in:** `docs/PERFORMANCE_REVIEW.md`

---

### 5. Testing Plan

**Create test scenarios for each workflow:**

**Label Automation:**
1. Create test issue
2. Add `state:done` label → verify issue closes
3. Close issue manually → verify `state:done` label added
4. Add `gate:needs-approval` → verify comment appears

**Nightly Decision Desk:**
1. Create 2 issues with `gate:needs-approval`
2. Create 1 issue with `state:blocked`
3. Manually trigger workflow via `workflow_dispatch`
4. Verify Decision Desk issue created with correct content

**WIP Limit:**
1. Create 4 issues with `state:build`
2. Try to add 5th → verify blocking works
3. Close 1 issue, verify limit now allows new one

**Weekly Cost Rollup:**
1. Add budget comments to several issues
2. Manually trigger workflow
3. Verify report aggregates correctly

**Document test plan in:** `docs/TESTING_PLAN.md`

---

### 6. Documentation Review

**Check existing docs:**

- [ ] `README.md` - mentions workflows?
- [ ] `docs/OPERATING_SYSTEM.md` - updated with automation info?
- [ ] `workflows/phase2-research-handoff.md` - implementation matches research?

**Create if missing:**
- [ ] `docs/AUTOMATION_GUIDE.md` - How the workflows work
- [ ] `docs/TROUBLESHOOTING.md` - Common issues and fixes

**Document findings in:** `docs/DOCUMENTATION_REVIEW.md`

---

### 7. Integration & Dependencies

**Check:**

- [ ] Workflows don't conflict with each other
- [ ] Label taxonomy matches what workflows expect
- [ ] Issue templates work with workflows
- [ ] No circular dependencies
- [ ] Workflows handle concurrent execution

**Example conflict to avoid:**
- Label automation closes issue
- WIP check tries to count it
- Race condition?

**Document findings in:** `docs/INTEGRATION_REVIEW.md`

---

### 8. Error Handling

**Check each workflow for:**

- [ ] Try-catch blocks where appropriate
- [ ] Graceful failure messages
- [ ] Continues on error vs. fails workflow (choose appropriately)
- [ ] Logs errors clearly for debugging
- [ ] Doesn't leave system in broken state on failure

**Document findings in:** `docs/ERROR_HANDLING_REVIEW.md`

---

### 9. Improvements & Optimizations

**Suggest:**

- Better ways to structure workflows
- Additional automation opportunities
- Edge cases not currently handled
- Performance optimizations
- User experience improvements

**Document in:** `docs/IMPROVEMENT_SUGGESTIONS.md`

---

### 10. Bug Report

**If you find bugs, document:**

**Format:**
```markdown
## Bug #X: [Title]

**File:** `.github/workflows/filename.yml`  
**Line:** XX  
**Severity:** Critical / High / Medium / Low

**Issue:**
[Description]

**Impact:**
[What breaks]

**Fix:**
[Suggested code change]

**Test:**
[How to verify fix works]
```

**Document in:** `docs/BUGS_FOUND.md`

---

## Output Format

### Create These Files:

1. `docs/OVERNIGHT_REVIEW_SUMMARY.md` - Executive summary
2. `docs/WORKFLOW_REVIEW.md` - Syntax checks
3. `docs/SECURITY_REVIEW.md` - Security findings
4. `docs/LOGIC_REVIEW.md` - Logic correctness
5. `docs/PERFORMANCE_REVIEW.md` - Performance analysis
6. `docs/TESTING_PLAN.md` - Test scenarios
7. `docs/DOCUMENTATION_REVIEW.md` - Doc gaps
8. `docs/INTEGRATION_REVIEW.md` - Integration issues
9. `docs/ERROR_HANDLING_REVIEW.md` - Error handling
10. `docs/IMPROVEMENT_SUGGESTIONS.md` - Enhancements
11. `docs/BUGS_FOUND.md` - Bug list (if any)

### Summary Format:

```markdown
# Overnight Review Summary

**Date:** 2026-02-25  
**Reviewer:** GitHub Copilot  
**Scope:** Phase 2 Automation Workflows

## Overall Assessment

**Status:** [Ready for Production / Needs Fixes / Major Issues]

**Critical Issues:** X  
**High Priority:** X  
**Medium Priority:** X  
**Low Priority:** X  

## Quick Wins (Fix These First)

1. [Issue]
2. [Issue]
3. [Issue]

## Long-Term Improvements

1. [Suggestion]
2. [Suggestion]

## Files Reviewed

- label-automation.yml: [Status]
- nightly-decision-desk.yml: [Status]
- wip-limit-check.yml: [Status]
- weekly-cost-rollup.yml: [Status]

## Recommendation

[Go-live / Fix critical issues first / Needs redesign]

## Next Steps for Perplexity

1. [Action]
2. [Action]
3. [Action]
```

---

## Execution Instructions

**Run this overnight:**

1. Read all 4 workflow files
2. Read phase2-research-handoff.md for requirements
3. Perform all 10 review categories
4. Create all documentation files
5. Commit everything to docs/ folder
6. Create summary issue or comment on Issue #13

**By morning, we should have:**
- Complete review documentation
- Bug list (if any)
- Testing plan
- Go/no-go recommendation

---

## Success Criteria

Review is complete when:
- [ ] All 10 review categories documented
- [ ] Summary file created
- [ ] All findings committed to repo
- [ ] Ready for Perplexity review in morning

**Start the review now. Take your time. Be thorough.**
