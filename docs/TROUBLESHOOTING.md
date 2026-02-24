# Troubleshooting

## Common Issues

### 1) Nightly Decision Desk fails in create step

**Symptom:** workflow fails with reference or undefined output errors.  
**Cause:** invalid output passing between `github-script` steps.  
**Fix:** emit outputs with `core.setOutput`; consume via `${{ steps.<id>.outputs.<name> }}`.

### 2) WIP comments appear on unrelated issues

**Symptom:** issue gets `WIP limit reached...` without receiving build/research label.  
**Cause:** workflow triggered on broad issue events.  
**Fix:** restrict to `issues.labeled` and guard for target labels.

### 3) Weekly rollup shows zero or low totals

**Symptom:** totals do not reflect recent budget updates.  
**Cause:** parser reads issue body, not comments; or data beyond first 100 issues not loaded.  
**Fix:** parse comments and add pagination.

### 4) Label operations fail with API error

**Symptom:** `Resource not found` / validation errors in logs.  
**Cause:** expected label missing in repo.  
**Fix:** create required labels listed in `docs/AUTOMATION_GUIDE.md`.

## Debug Checklist

1. Confirm event payload/action in run logs.
2. Confirm required labels exist exactly (case-sensitive).
3. Re-run via `workflow_dispatch` with minimal test data.
4. Add temporary debug logging (`core.info`) in scripts.
