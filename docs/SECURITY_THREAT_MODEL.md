# Security Threat Model

## Trust Boundaries
- External issue authors.
- Labeling/triage users.
- GitHub Actions runner with `issues:write`.

## Key Threats
1. Malicious issue body manipulates cost parsing and dashboards (Medium).
2. Label abuse to force close/block transitions (High).
3. Workflow poisoning through PR changes to workflow YAML (High).
4. Resource exhaustion via event storms/label toggling (Medium).
5. Privilege escalation through over-broad maintainer permissions (Medium).

## Mitigations
- CODEOWNERS + required review for `.github/workflows/*`.
- Label allowlist transition policy.
- Rate limiting/idempotency comments.
- Actor role checks before state-changing operations.
- Signed release process for workflow changes.
