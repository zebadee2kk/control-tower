# Handoff Automation Limitations

This document records any problems or manual steps encountered during the execution of the Issue #11 Handoff workflow, so that a future agent or user (e.g., Perplexity) can address them.

## Problems/Manual Steps

### 1. Missing Labels
- See docs/MISSING_LABELS.md for a list of labels that were not created by the bootstrap script.
- Possible causes: API rate limits, script errors, or permission issues.
- Manual creation of missing labels may be required.

### 2. Project Board Creation & Configuration
- Creating and configuring a GitHub Project v2 board (columns, custom fields) cannot be fully automated via CLI/API as of February 2026.
- Manual steps required:
  - Create the board via the GitHub web UI.
  - Add columns: Backlog, In Progress, Awaiting Decision, Blocked, Done.
  - Add custom fields: Priority (P0, P1, P2, P3), Gate (Allowed, Needs Approval, Paused), Budget Cap, Spend-to-Date.
- Record the project board URL for documentation.

### 3. Project Number Required
- Linking issues to the project via CLI requires the project number, which is only available after manual creation.
- Replace <PROJECT_NUMBER> in scripts/commands with the actual number from the project URL.

## Next Steps
- After manual steps are completed, proceed with CLI-automatable tasks: linking issues, applying labels, closing issues, and documenting completion.

---

This file should be updated as further limitations or manual requirements are discovered.
