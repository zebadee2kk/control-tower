# Architecture Analysis

## Rating: C+

## What Works
- Clear label-driven state machine concept.
- Human decision gate (`gate:needs-approval`) separates autonomous flow from approvals.
- GitHub issues provide durable audit trail and low operational burden.

## Structural Weaknesses
1. **State machine is implicit, not enforced.** Multiple state labels can coexist.
2. **No canonical transition controller.** Independent workflows can conflict.
3. **Global scans on every event.** `listForRepo` per trigger does not scale.
4. **No anti-entropy job.** Invalid states can persist indefinitely.
5. **No tenancy/isolation model.** All issues treated equally (feature, report, maintenance).

## Invalid-State Risks
- `state:build` + `state:blocked` + `state:done` can coexist.
- Closing logic can set `state:done` without clearing prior labels.

## Scale Projections
- **100 issues:** workable with occasional noise.
- **1000 issues:** truncation due to no pagination; automation decisions become statistically wrong.

## Recommended Architecture Changes
1. Implement a **single transition workflow** with explicit allowed transitions matrix.
2. Introduce **state reconciliation** nightly job (authoritative repair).
3. Build reusable `octokit-paginate` helper.
4. Add lightweight metadata contract in issue body/front matter.
5. Add workflow `concurrency` and idempotency keys.
