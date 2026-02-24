# Code Quality Audit

## Grade: C

## Findings
- Repeated Octokit patterns with no shared helper.
- Missing `await` and missing explicit error handling in all workflows.
- Hard-coded constants (`maxWip`, overrun threshold).
- Limited comments on failure behavior.
- No linting gate for workflow files.

## Actions
- Add `rhysd/actionlint` CI job.
- Add repository-level constants through `vars`.
- Adopt JS style conventions in `github-script` blocks.
