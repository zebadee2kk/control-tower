# Changelog

All notable changes to `control-tower` are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.3.0] — 2026-03-08

Phase 3A: Python decision layer and enhanced GitHub Actions workflow.

### Added
- Python Decision Desk layer (`src/`) — AI-powered project analysis and prioritisation
- `feat/enhanced-desk-workflow`: wire Python layer into enhanced Decision Desk GitHub Actions workflow
- Ollama integration with guard against empty `OLLAMA_HOST` (fallback to disabled)
- Cost tracker integration within Decision Desk pipeline

### Fixed
- Empty `OLLAMA_HOST` environment variable causing crash in `_call_ollama` (PR #67)

---

## [0.2.0] — 2026-02-01

Phase 2: ecosystem documentation and integration patterns.

### Added
- `docs/ECOSYSTEM_ARCHITECTURE.md` — complete validated architecture across all managed repos
- `docs/INTEGRATION_PATTERNS.md` — documented how ecosystem components connect
- `docs/DEPLOYMENT.md` — deployment guide (where things run)
- `docs/PHASE_3_ROADMAP.md` — Phase 3 implementation plan
- Bug tracker documentation reconciled and Phase 2 completion documented (PR #58)
- VSCode Claude copy-paste prompt for session setup
- Quick checklist for Phase 2 documentation

### Changed
- README restructured for new contributors and AI assistants
- Phase badge updated: Phase 1 → Phase 2

---

## [0.1.0] — 2025-12-01

Phase 1: initial control plane with 9pm Decision Desk.

### Added
- Initial `control-tower` repository setup
- **9pm Decision Desk** — nightly GitHub Actions workflow for project prioritisation
- `decisions/` directory for Decision Desk output records
- `workflows/` directory for reusable GitHub Actions workflows
- `scripts/` utility scripts
- `README.md` — project overview, quick start for contributors and AI assistants
- `requirements.txt` / `requirements-dev.txt` — Python dependencies
- MIT License

---

## Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| [0.3.0] | 2026-03-08 | Phase 3A — Python decision layer, enhanced workflow, Ollama integration |
| [0.2.0] | 2026-02-01 | Phase 2 — ecosystem architecture and integration documentation |
| [0.1.0] | 2025-12-01 | Phase 1 — initial control plane and Decision Desk |

---

[Unreleased]: https://github.com/zebadee2kk/control-tower/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/zebadee2kk/control-tower/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/zebadee2kk/control-tower/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/zebadee2kk/control-tower/releases/tag/v0.1.0
