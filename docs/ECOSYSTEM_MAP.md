# Ecosystem Map

> Last audited: 2026-03-08

## Purpose

Track all repositories and projects in your portfolio. This is your central registry for understanding what exists, what's active, and what needs attention.

---

## Repository Registry

### Control Tower
- **Repo:** [zebadee2kk/control-tower](https://github.com/zebadee2kk/control-tower)
- **Purpose:** GitHub-native meta control plane for AI-assisted projects; orchestrates all other repos via nightly Decision Desk workflow
- **Status:** 🟢 Active
- **Open Issues:** 6
- **Next Steps:** Progress through Phase 3A roadmap; wire up live integrations with portfolio-management and ai-cost-tracker
- **Tags:** `governance`, `orchestration`, `core`
- **Consolidation:** Hub — not a candidate for merging
- **Last Updated:** 2026-03-08

---

### ai-cost-tracker
- **Repo:** [zebadee2kk/ai-cost-tracker](https://github.com/zebadee2kk/ai-cost-tracker)
- **Purpose:** AI-powered cost tracking and budget management for multi-model API usage across the entire ecosystem
- **Status:** 🟢 Active
- **Open Issues:** 5
- **Next Steps:** Complete integration hooks for control-tower and portfolio-management; stabilise API surface
- **Tags:** `cost-control`, `budget`, `ai`, `integration`
- **Consolidation:** Core shared service — keep standalone
- **Last Updated:** 2026-03-08

---

### portfolio-management
- **Repo:** [zebadee2kk/portfolio-management](https://github.com/zebadee2kk/portfolio-management)
- **Purpose:** AI-powered GitHub portfolio management system — automated repo scanning, project prioritisation, and cross-repo coordination
- **Status:** 🟢 Active
- **Open Issues:** 0
- **Next Steps:** Connect to control-tower Decision Desk; add cost reporting via ai-cost-tracker
- **Tags:** `portfolio`, `automation`, `ai`, `orchestration`
- **Consolidation:** Consider eventual merge into control-tower as a module once API stabilises
- **Last Updated:** 2026-03-08

---

### sentinelforge
- **Repo:** [zebadee2kk/sentinelforge](https://github.com/zebadee2kk/sentinelforge)
- **Purpose:** Secure containment platform for running autonomous AI agents with strict governance, auditing, and observability (PLpgSQL / PostgreSQL backend)
- **Status:** 🟢 Active — early stage (created 2026-03-06)
- **Open Issues:** 0
- **Next Steps:** Define agent-containment API; integrate cost governance via ai-cost-tracker; create initial issues
- **Tags:** `security`, `ai-agents`, `governance`, `observability`
- **Consolidation:** Specialist domain — keep standalone; flag for **Repo Recon** to assess architecture depth
- **Last Updated:** 2026-03-08

---

### kynee
- **Repo:** [zebadee2kk/kynee](https://github.com/zebadee2kk/kynee)
- **Purpose:** KYNEĒ — AI-assisted portable security assessment platform for authorised penetration testing and red team operations
- **Status:** 🟡 Maintenance — active issue backlog, no recent commits
- **Open Issues:** 8
- **Next Steps:** Triage 8 open issues; decide on active development vs maintenance mode; flag for **Repo Recon**
- **Tags:** `security`, `pentest`, `red-team`, `ai`
- **Consolidation:** Specialist domain — keep standalone, but review overlap with sentinelforge
- **Last Updated:** 2026-02-25

---

### ai-powertools
- **Repo:** [zebadee2kk/ai-powertools](https://github.com/zebadee2kk/ai-powertools)
- **Purpose:** Collection of "Multiplier Components" and AI-driven workflow tools (includes Model Intelligence Framework, security helpers, tier-aware routing)
- **Status:** 🟡 Maintenance — branch strategy recently stabilised, no open issues
- **Open Issues:** 0
- **Next Steps:** Review overlap with zebra-ecosystem model registry; consider promoting stable modules to other repos
- **Tags:** `ai`, `tooling`, `model-intelligence`, `productivity`
- **Consolidation:** ⚠️ Overlaps with zebra-ecosystem model registry — evaluate merge
- **Last Updated:** 2026-02-28

---

### best-practice-repo-template
- **Repo:** [zebadee2kk/best-practice-repo-template](https://github.com/zebadee2kk/best-practice-repo-template)
- **Purpose:** Ultimate GitHub Repository Template — security playbooks, CI/CD patterns, scalable project management scaffolding
- **Status:** 🟡 Maintenance — useful reference but no active feature development
- **Open Issues:** 5
- **Next Steps:** Triage 5 open issues; ensure template reflects current control-tower conventions; consider tagging as a stable reference
- **Tags:** `templates`, `best-practices`, `ci-cd`, `security`, `governance`
- **Consolidation:** Keep as standalone template; low priority for active development
- **Last Updated:** 2026-02-24

---

### zebadee2kk (Profile)
- **Repo:** [zebadee2kk/zebadee2kk](https://github.com/zebadee2kk/zebadee2kk)
- **Purpose:** GitHub profile README — personal portfolio and public-facing identity ("Architecting Efficiency & AI-First Systems")
- **Status:** 🟡 Maintenance — updated recently but no development cadence needed
- **Open Issues:** 0
- **Next Steps:** Keep in sync with active projects; update featured repos to reflect current ecosystem
- **Tags:** `profile`, `portfolio`, `public`
- **Consolidation:** Not a candidate — unique GitHub profile repo
- **Last Updated:** 2026-03-08

---

### zebra-ecosystem
- **Repo:** [zebadee2kk/zebra-ecosystem](https://github.com/zebadee2kk/zebra-ecosystem)
- **Purpose:** AI-powered Python ecosystem with integrated security, cost control, and model intelligence frameworks — modular architecture for homelab automation, trading systems, and AI agents
- **Status:** ⚪ Evaluating — no open issues, no activity since Feb 2026, likely early prototype
- **Open Issues:** 0
- **Next Steps:** Determine whether this is superseded by ai-powertools + portfolio-management + control-tower; flag for **Repo Recon**; **archival candidate** if no active roadmap
- **Tags:** `ecosystem`, `model-registry`, `homelab`, `trading`, `ai`
- **Consolidation:** ⚠️ High overlap with ai-powertools and control-tower — **strong merge/archive candidate**
- **Last Updated:** 2026-02-21

---

## Status Definitions

- 🟢 **Active** — Under active development
- 🟡 **Maintenance** — Stable, occasional updates
- 🔴 **Archived** — No longer maintained
- 🔵 **Planned** — Not yet created
- ⚪ **Evaluating** — Exploring viability / potentially stale

---

## Consolidation Candidates

| Repo | Recommendation | Rationale |
|------|---------------|-----------|
| `zebra-ecosystem` | 🔴 Archive or merge into `ai-powertools` | No activity since Feb 21; model registry duplicated in ai-powertools |
| `portfolio-management` | Consider future merge into `control-tower` | Functionality naturally belongs in hub once API is stable |
| `ai-powertools` + `zebra-ecosystem` | Evaluate merging model registry | Both contain model intelligence / registry code |

---

## Archival Candidates

| Repo | Reason |
|------|--------|
| `zebra-ecosystem` | No commits or issues since Feb 2026; functionality covered by ai-powertools and control-tower |

---

## Repo Recon Flags

Repos requiring deeper analysis (dedicated Repo Recon issues to create):

| Repo | Flag Reason |
|------|-------------|
| `sentinelforge` | New repo (5 days old) — architecture and scope need documenting |
| `kynee` | 8 open issues, no recent commits — needs triage and roadmap decision |
| `zebra-ecosystem` | Determine active vs abandoned; decide merge/archive path |
| `ai-powertools` | Review model registry overlap with zebra-ecosystem before any merge |

---

## Dependency Map

```
control-tower
├── portfolio-management  (repo scanning & prioritisation)
├── ai-cost-tracker       (budget tracking & cost governance)
└── sentinelforge         (agent execution governance)

sentinelforge
└── ai-cost-tracker       (cost metering for agent runs)

portfolio-management
└── ai-cost-tracker       (cost reporting)

ai-powertools
└── zebra-ecosystem       (model registry — overlap, to be resolved)
```

---

## Portfolio Metrics

| Metric | Value |
|--------|-------|
| **Total Repositories** | 9 |
| **Active** 🟢 | 4 (control-tower, ai-cost-tracker, portfolio-management, sentinelforge) |
| **Maintenance** 🟡 | 4 (kynee, ai-powertools, best-practice-repo-template, zebadee2kk profile) |
| **Evaluating / Stale** ⚪ | 1 (zebra-ecosystem) |
| **Archived** 🔴 | 0 |
| **Archival Candidates** | 1 (zebra-ecosystem) |
| **Repo Recon Issues to Create** | 4 |
| **Total Open Issues (ecosystem)** | 24 |
| **Weekly Time Commitment** | 3-5 hours |

---

## Template for Adding New Repos

### [Repo Name]
- **Repo:** [owner/repo](https://github.com/owner/repo)
- **Purpose:** Brief description
- **Status:** 🟢 Active / 🟡 Maintenance / 🔴 Archived / 🔵 Planned / ⚪ Evaluating
- **Open Issues:** N
- **Next Steps:** What needs to happen
- **Tags:** Categorisation labels
- **Consolidation:** Merge/archive candidates or "keep standalone"
- **Last Updated:** YYYY-MM-DD

---

**Update this map weekly as part of your operating rhythm.**