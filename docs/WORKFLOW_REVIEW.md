# Workflow Syntax & Correctness Review

**Date:** 2026-02-25  
**Scope:** `.github/workflows/*.yml`

## Validation Method

- Parsed each YAML file with Ruby's built-in YAML parser.
- Performed manual schema/semantics checks for triggers, permissions, job structure, and `if:` expressions.

## Results by Workflow

### 1) `label-automation.yml`
- ✅ Valid YAML syntax.
- ✅ Required top-level keys present: `name`, `on`, `permissions`, `jobs`.
- ✅ Trigger set is coherent for label/state automation (`labeled`, `unlabeled`, `closed`, `workflow_dispatch`).
- ⚠️ Uses `actions/github-script@v6` instead of current `@v7`.
- ⚠️ API calls are not awaited, which can cause non-deterministic completion.

### 2) `nightly-decision-desk.yml`
- ✅ Valid YAML syntax.
- ✅ Required top-level keys present.
- ✅ Schedule cron (`0 21 * * *`) and `workflow_dispatch` are defined.
- ❌ Step-to-step data passing is invalid: `steps.query.outputs` is referenced directly inside JavaScript; this object is not available in the script runtime.
- ❌ `query` step does not set explicit outputs (`core.setOutput`) for downstream usage.
- ⚠️ API calls are not awaited.

### 3) `wip-limit-check.yml`
- ✅ Valid YAML syntax.
- ✅ Required top-level keys present.
- ⚠️ Trigger set is broader than requirement (includes `unlabeled`, `opened`, `reopened`), causing unnecessary runs.
- ⚠️ API calls are not awaited.

### 4) `weekly-cost-rollup.yml`
- ✅ Valid YAML syntax.
- ✅ Required top-level keys present.
- ✅ Weekly cron (`0 18 * * 0`) and `workflow_dispatch` present.
- ⚠️ API calls are not awaited.

## Permissions Review

All workflows define:
```yaml
permissions:
  issues: write
  contents: read
```
This is acceptable and close to least privilege for current behavior.

## Summary

- YAML syntax is valid across all four workflows.
- Major correctness defects exist in `nightly-decision-desk.yml` output handling.
- All workflows should standardize on `actions/github-script@v7` and explicit `await` on API operations.
