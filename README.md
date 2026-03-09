# Control Tower

**AI-Orchestrated Project Governance Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Status](https://img.shields.io/badge/status-active_development-blue.svg)

---

## The Problem

Running multiple AI-assisted projects simultaneously creates a governance problem. Work gets duplicated, costs spiral across multiple AI providers, priorities shift without visibility, and there’s no single source of truth for what’s actually in progress.

This problem is worse at scale — and it’s exactly the kind of operational overhead that kills velocity.

---

## What Control Tower Does

Control Tower is a meta-control plane that brings structure, prioritisation, and cost governance to a portfolio of AI-powered projects. It treats GitHub as the operational backbone and AI as the analysis layer — not the other way around.

Key capabilities:

- **Nightly Decision Desk** — automated nightly analysis of all active projects, surfacing priority actions and blockers
- **AI cost governance** — real-time tracking and budget caps across all AI provider usage
- **Cross-repo orchestration** — single view across 16+ repositories with dependency tracking
- **WIP limits** — enforced work-in-progress constraints to prevent context overload
- **Automated prioritisation** — AI-driven scoring of issues and projects against defined objectives
- **Human-in-the-loop** — recommendations surface daily; a human approves, rejects, or adjusts (< 5 minutes)

---

## The Philosophy

GitHub is the source of truth. AI assists — it doesn’t decide. Every recommendation requires human review. Costs are tracked and capped. Work flows through defined gates.

This is what responsible AI-assisted operations looks like in practice.

---

## Who It's For

- Engineering leads managing multiple concurrent AI-assisted workstreams
- IT leaders who need governance and auditability across AI tool usage
- Organisations building AI-first operations who need structure, not chaos

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Orchestration | GitHub Actions (nightly workflows) |
| Analysis | Python 3.11+, Azure OpenAI, local LLMs |
| Cost Tracking | ai-cost-tracker (REST API) |
| Infrastructure | VPS + Homelab Docker |
| Project Management | GitHub Projects v2 |

---

## Status

Active development. Decision Desk, cost tracking, label automation, and WIP limits are operational. Full 16-repo portfolio view and cross-repo dependency tracking are in active build.

---

## About

Control Tower is built and maintained by [Richard Ham](https://richardham.co.uk) — Fractional IT & Security Leader with 25 years of enterprise IT experience. It was designed to solve a real operational problem: how do you maintain governance and velocity when AI is involved in every project simultaneously?

---

## License

MIT License — see [LICENSE](LICENSE)
