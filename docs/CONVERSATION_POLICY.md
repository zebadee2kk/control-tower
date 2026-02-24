# Conversation Policy

This document explains where to stash discussion artifacts while working
inside the Control Tower.  Clear boundaries keep the repository clean and
everything governed.

## Vaults & Destinations

### 🗂 Local / Working Vault
- Raw chat transcripts and AI sessions
- Brainstorms, ephemeral notes, unstructured drafts
- Tool outputs that are noisy or sensitive

> **Location:** your laptop/branch; *never commit these directly.*

### 🥇 Gold Vault (`gold/`)
Polished, high–value knowledge that deserves longevity.

**Allowed content**
- Research memos and architecture deep dives
- Decision summaries and lesson‑learned writeups
- Reusable document templates or checklists
- Anything that others can read independently

**Quality bar**
1. Self‑contained and understandable without raw chat.
2. Free of secrets or proprietary data.
3. Follows the naming convention `YYYY-MM-DD-topic-name.md`.

> Raw or unfinished material stays local until it is refined.

### 🐙 GitHub (Issues & PRs)
GitHub is the control plane for governance and work tracking.

- All work **must** start with an issue (idea‑intake, decision‑required,
  repo‑recon, etc.).
- Use issue labels from the taxonomy (`state:*`, `p0`‑`p3`, `gate:*`).
- Cost governance, decision gates, and resource estimates belong here.
- PRs use the standard template with Why/What/Risk/Checklist.

## Why the separation?
Keeping conversations local prevents noise in the repo.
The gold vault accumulates only curated artifacts, and GitHub issues
capture concrete commitments and approvals.

> Treat this policy as part of the operating system: follow it to
maintain clarity and avoid wasted effort.