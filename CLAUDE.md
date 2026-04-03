# CLAUDE.md — control-tower

## What this repo is for

**One sentence:** control-tower is the cross-repo orchestration hub — it routes tasks between repos, coordinates agent handoffs, and maintains the master portfolio state.

**Non-goals:** control-tower must NOT contain application logic, feature code, or repo-specific automation. Those belong in their respective repos. If a task is about making something work in a specific repo, route it there.

**Tier:** ACTIVE

---

## Read this first

Before doing anything, read these files in order:

1. `README.md` — routing model and repo map
2. `docs/portfolio-map.md` — current ACTIVE / MAINTAIN / PARKED repo tiers (create stub if missing)
3. `docs/handoff-protocol.md` — how task packets are structured and passed between repos (create stub if missing)
4. Open issues labelled `blocked` or `routing-decision`

---

## Session start protocol

**Do not write code immediately.** Follow this order:

1. **Explore** — read the files above, run `git log --oneline -20`.
2. **Plan** — identify which repos are affected by any proposed change.
3. **Confirm** — always get approval before any change that touches routing logic or the portfolio map.
4. **Implement** — one repo concern per commit.
5. **Validate** — check that no dependent repos are broken by the routing change.
6. **Handoff** — write session summary.

---

## Task routing

| Task type | Destination |
|---|---|
| Feature work in a specific repo | Route to that repo — do not implement here |
| Portfolio state changes | Update `docs/portfolio-map.md` + open tracking issue |
| Agent handoff spec changes | Update `docs/handoff-protocol.md` |
| Cross-repo dependency tracking | Open issue here with affected repos listed |
| Destructive routing changes | Human approval required |
| Scheduling / triggers | n8n workflow — not Python here |
| Secrets | Vaultwarden — never in code |

---

## Approved commands

```bash
git log --oneline -20
git diff HEAD
cat docs/portfolio-map.md
cat docs/handoff-protocol.md
python -m pytest tests/ --dry-run
```

**Never run without explicit approval:**
- Any command that writes to another repo
- Any `git push --force`
- Any command that modifies routing config affecting production workflows
- Any destructive file operation

---

## Commit and branch rules

- Branch naming: `route/`, `docs/`, `chore/`, `fix/`
- Commit messages: imperative, present tense
- One routing concern per commit
- Never commit directly to `main`
- PRs require: description of routing impact, affected repos listed, rollback plan

---

## Definition of done

A task is complete when ALL of the following are true:

- [ ] PR open on branch
- [ ] Portfolio map updated if repo tier changed
- [ ] Dependent repos notified via issue or PR comment
- [ ] Rollback notes in PR
- [ ] Linked issue updated or closed
- [ ] Handoff summary written

---

## Danger zones — never touch without explicit approval

- `docs/handoff-protocol.md` — changes here break agent-to-agent task passing
- `docs/portfolio-map.md` — source of truth for repo tiers; wrong tiers cause misdirected work
- Any routing config referencing production webhook URLs or API tokens
- Any file that affects how HamOS dispatches tasks to agents

---

## Output contract

At the end of every session or significant task, produce a handoff in this exact format:

```
## Session summary — [date]

**Completed:**
- [what was done]

**Files changed:**
- [path] — [one-line reason]

**Repos affected:**
- [list any repos whose behaviour is changed by this work]

**Skipped / deferred:**
- [what was not done and why]

**Risks / watch points:**
- [anything that could break or needs monitoring]

**Next action:**
- [the single most important thing to do next]
```

---

## Architecture snapshot

control-tower is primarily a documentation-and-routing repo. It holds the canonical portfolio map, handoff protocol, and cross-repo dependency graph. HamOS and n8n workflows reference it to route tasks correctly. Agent sessions use it to understand scope boundaries before starting work. Python tooling in this repo is limited to orchestration helpers, not application logic.

---

## Repo-local glossary

| Term | Meaning |
|---|---|
| Portfolio map | The master list of all repos with their ACTIVE/MAINTAIN/PARKED tier |
| Handoff protocol | The structured format for passing task packets between repos and agents |
| Routing | Deciding which repo or agent should own a given piece of work |

---

_Last updated: 2026-04-03_
