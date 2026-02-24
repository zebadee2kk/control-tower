# Issue #11 Handoff Package

**Issue:** [Document bootstrap results and create Project board manually](https://github.com/zebadee2kk/control-tower/issues/11)

**Status:** Ready for execution  
**Assigned to:** VS Code/Copilot  
**Budget:** 30 minutes, £0

---

## Context

The bootstrap script successfully created all 16 labels but could not create the GitHub Project v2 board via CLI (API limitation).

**Bootstrap Script Results:**
- ✅ Labels Created/Updated: 16/16
- ⚠️ Project Board: Needs manual creation

---

## Tasks to Execute

### Task 1: Verify Label Creation

**Command:**
```bash
gh label list -R zebadee2kk/control-tower | wc -l
```

**Expected:** 17 labels (16 new + 1 existing `state:triage`)

**Action:** Run command and report count.

---

### Task 2: Create GitHub Project Board

**Manual steps required:**

1. Go to: https://github.com/zebadee2kk/control-tower/projects
2. Click "New project"
3. Select template: "Board"
4. Name: "Control Tower"
5. Click "Create"

**Action:** Complete these steps in browser, then note the project URL.

---

### Task 3: Configure Project Board

**Add Columns (in order):**
1. Backlog
2. In Progress
3. Awaiting Decision
4. Blocked
5. Done

**Add Custom Fields:**

1. **Priority** (Single select)
   - Options: P0, P1, P2, P3

2. **Gate** (Single select)
   - Options: Allowed, Needs Approval, Paused

3. **Budget Cap** (Text)

4. **Spend-to-Date** (Text)

**Action:** Configure via Project settings UI.

---

### Task 4: Link All Issues to Project

**Once project is created, run:**
```bash
for i in {1..11}; do
  gh project item-add <PROJECT_NUMBER> --owner zebadee2kk --url https://github.com/zebadee2kk/control-tower/issues/$i
done
```

**Note:** Replace `<PROJECT_NUMBER>` with actual project number from URL.

**Action:** Execute command to link all issues.

---

### Task 5: Apply Labels to Existing Issues

**Run these commands:**
```bash
gh issue edit 1 -R zebadee2kk/control-tower --add-label "state:planning"
gh issue edit 2 -R zebadee2kk/control-tower --add-label "state:planning,p1"
gh issue edit 3 -R zebadee2kk/control-tower --add-label "state:planning,p1"
gh issue edit 4 -R zebadee2kk/control-tower --add-label "state:research,p1"
gh issue edit 5 -R zebadee2kk/control-tower --add-label "state:done"
gh issue edit 6 -R zebadee2kk/control-tower --add-label "state:planning,p1"
gh issue edit 7 -R zebadee2kk/control-tower --add-label "state:planning,p2"
gh issue edit 8 -R zebadee2kk/control-tower --add-label "state:research,p1"
gh issue edit 9 -R zebadee2kk/control-tower --add-label "state:done"
gh issue edit 10 -R zebadee2kk/control-tower --add-label "state:awaiting-decision,gate:needs-approval,p0"
gh issue edit 11 -R zebadee2kk/control-tower --add-label "state:planning,p1"
```

**Action:** Execute all commands.

---

### Task 6: Close Completed Issues

**Run:**
```bash
gh issue close 5 -R zebadee2kk/control-tower -c "✅ Templates created and committed"
gh issue close 9 -R zebadee2kk/control-tower -c "✅ Conversation policy documented"
```

**Action:** Close issues #5 and #9.

---

### Task 7: Document Completion

**Add comment to Issue #11:**
```bash
gh issue comment 11 -R zebadee2kk/control-tower --body "## Completion Report

✅ **Task 1:** Label count verified: [X] labels
✅ **Task 2:** Project board created: [URL]
✅ **Task 3:** Board configured with 5 columns and 4 custom fields
✅ **Task 4:** All 11 issues linked to project
✅ **Task 5:** Labels applied to all issues
✅ **Task 6:** Issues #5 and #9 closed

**Time spent:** [X] minutes

**v1 Control Tower setup complete. System operational.**"
```

**Then close Issue #11:**
```bash
gh issue close 11 -R zebadee2kk/control-tower
```

---

## Acceptance Criteria

- [ ] Label count verified (17 total)
- [ ] Project board created and configured
- [ ] All columns present
- [ ] Custom fields added
- [ ] All 11 issues linked to project
- [ ] Labels applied to all issues
- [ ] Issues #5, #9, #11 closed
- [ ] Completion documented

---

## Output

**Expected deliverables:**
- Project board URL
- Screenshot or confirmation of setup
- Completion comment on Issue #11
- Time tracking data

---

## Next Steps After Completion

1. Create tonight's Decision Desk issue
2. Make first decisions (pilot project selection)
3. Begin operational workflow

**System will be 100% operational after this handoff.**
