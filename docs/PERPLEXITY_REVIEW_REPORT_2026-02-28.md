# Perplexity Pickup Report — Security, Best Practices, and Documentation Review

**Date:** 2026-02-28  
**Scope reviewed:** Recent work around Bug #7 and associated handoff updates (`14520f3`, `f6af077`, `3e737ac`)  
**Primary reviewer:** Codex (GPT-5.2-Codex)

---

## Executive Summary

Recent Bug #7 work is directionally good and production-usable, with a meaningful reliability improvement in Decision Desk retention behavior. The workflow now closes older Decision Desk issues before opening a new one and filters by title to reduce accidental closure of unrelated issues.

However, there are still **important hardening gaps** before calling the full automation stack "secure + best practice complete":

1. **GitHub Actions are version-tag pinned (`@v6`) instead of full commit SHA pinned** (supply-chain hardening gap).
2. **WIP workflow can still fail noisily** when `removeLabel` is attempted on a label that was removed concurrently.
3. **Documentation drift exists** between `PHASE_2_5_STATUS.md` and `BUGS_FOUND.md` on which bugs are fully resolved.
4. **No idempotency guard** in weekly rollup (operational quality risk).

---

## What Was Reviewed

### Commits
- `14520f3` — workflow logic update in `.github/workflows/nightly-decision-desk.yml`
- `f6af077` — merge of PR #49
- `3e737ac` — documentation and handoff updates in `docs/`

### Files examined
- `.github/workflows/nightly-decision-desk.yml`
- `.github/workflows/wip-limit-check.yml`
- `.github/workflows/weekly-cost-rollup.yml`
- `.github/workflows/label-automation.yml`
- `docs/HANDOFF_2026-02-28_BUG7.md`
- `docs/PHASE_2_5_STATUS.md`
- `docs/BUGS_FOUND.md`

---

## Findings

### 1) Nightly Decision Desk change quality (Bug #7)
**Status:** ✅ Good improvement

- Querying and closing previous Decision Desk issues before creating the new one is correct and removes a known ordering hazard.
- Filtering closed candidates by title prefix (`Decision Desk`) is a sensible protective measure.
- `state_reason: completed` improves auditability of closure cause.

**Residual caution:**
- Filtering by title prefix is string-convention dependent; robust but not fully canonical. Label + metadata strategy would be stronger long term.

---

### 2) Security hardening posture
**Status:** ⚠️ Needs improvement

- All workflows use `actions/github-script@v6` tag pinning (not immutable SHA pinning).
- Current permissions are narrower than default and acceptable (`issues: write`, `contents: read`), but `contents: read` may be unnecessary in some workflows and can be removed where not used.

**Recommendation:**
- Pin each third-party action to a full SHA.
- Reduce permissions to least privilege per workflow (drop `contents: read` unless explicitly needed).

---

### 3) Operational robustness
**Status:** ⚠️ Mixed

- `nightly-decision-desk.yml`: improved stability.
- `wip-limit-check.yml`: still vulnerable to a race where `removeLabel` can fail if the label is already absent.
- `weekly-cost-rollup.yml`: no weekly idempotency check; repeated manual or retried runs create duplicates.

**Recommendation:**
- Guard `removeLabel` with a current-label existence check just before mutation.
- Add week-keyed idempotency (`Weekly Cost Rollup (YYYY-WW)` existence query before create).

---

### 4) Documentation quality and consistency
**Status:** ⚠️ Needs alignment

- `PHASE_2_5_STATUS.md` states broad bug-fix completion.
- `BUGS_FOUND.md` still lists high-priority bugs as open (#4, #5, #6) without explicit status reconciliation.
- `HANDOFF_2026-02-28_BUG7.md` is helpful and actionable.

**Recommendation:**
- Harmonize bug status language across docs with one canonical tracker.
- Add “verified in file + date + evidence link” for each bug line item.

---

## Priority Actions for Perplexity

### P0 — Security / governance
1. Pin all `uses:` actions to immutable SHAs.
2. Re-audit workflow permissions and remove unused scopes.

### P1 — Reliability
3. Implement defensive check for `removeLabel` race in WIP workflow.
4. Add idempotency to weekly rollup creation.

### P1 — Documentation integrity
5. Reconcile `BUGS_FOUND.md` and `PHASE_2_5_STATUS.md` into one source of truth.
6. Add verification metadata for each bug status change.

---

## Suggested Execution Order

1. **Hardening PR:** action SHA pinning + permissions minimization.
2. **Reliability PR:** WIP `removeLabel` guard + weekly rollup idempotency.
3. **Docs PR:** bug ledger reconciliation + evidence references.

---

## Ready-to-Use Prompt for Perplexity

Use this to continue work:

> Review `.github/workflows/*.yml` and implement a hardening pass: pin `actions/github-script` to immutable SHA, minimize token permissions per workflow, and preserve existing behavior. Then patch `wip-limit-check.yml` to avoid failures when `removeLabel` is called on missing labels (race-safe check), and patch `weekly-cost-rollup.yml` with week-based idempotency so reruns do not duplicate issues. Finally, update `docs/BUGS_FOUND.md` and `docs/PHASE_2_5_STATUS.md` so bug statuses are consistent, evidence-backed, and date-stamped.

---

## Review Verdict

- **Bug #7 changes:** Approved ✅
- **Overall stack security/best-practice posture:** Conditionally approved pending hardening tasks ⚠️
- **Documentation quality:** Good but inconsistent; reconciliation required ⚠️
