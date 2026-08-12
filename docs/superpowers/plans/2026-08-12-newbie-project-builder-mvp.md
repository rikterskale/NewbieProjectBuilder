# Newbie Project Builder MVP Implementation Plan

> **Goal:** Implement the approved safety-first Windows/Linux project builder in a reviewable
> feature branch with tests, documentation, CI, and no automatic merge.

**Architecture:** Thin native launchers start a shared Python package. Focused services own
host detection, commands, redaction, logging, package plans, project generation, GitHub
operations, integrations, support, state, and backups.

**Tech stack:** Python 3.11+, PowerShell, Bash, Git, GitHub CLI, pytest, Ruff, mypy, Bandit,
pip-audit, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-12-newbie-project-builder-design.md`

## Completed work units

- [x] Create typed domain models and builder-owned path layout.
- [x] Implement secret redaction and stable beginner error catalog.
- [x] Implement redacted operation logs and argument-array command execution.
- [x] Implement Windows/Linux host discovery and read-only preflight checks.
- [x] Implement exact WinGet and supported APT installation plans.
- [x] Implement durable workflow state and backup services.
- [x] Implement project-name validation, preview, generation, and Git initialization.
- [x] Implement Python CLI and planning-first project templates.
- [x] Implement browser-based GitHub CLI boundary and safe publication rules.
- [x] Implement Codex/Superpowers status and Agency Agents core installer.
- [x] Implement sanitized support bundles and marked cleanup.
- [x] Implement interactive menu and noninteractive CLI.
- [x] Add Windows and Linux launchers and diagnostic helpers.
- [x] Add unit and integration-style tests with branch coverage gate.
- [x] Add pinned cross-platform CI, security checks, Dependabot, and check scripts.
- [x] Add beginner, architecture, security, status, roadmap, and contribution documentation.

## Verification commands

```bash
python -m compileall -q src
PYTHONPATH=src python -m pytest
python -m ruff check .
python -m mypy src
python -m bandit -c pyproject.toml -r src
python -m pip_audit
python -m build
bash -n start-linux.sh scripts/*.sh
```

## Publish gate

- [ ] Review the complete file list and local diff.
- [ ] Confirm no cache, virtual-environment, coverage-data, credential, or unrelated file is
  included.
- [ ] Create `agent/build-cross-platform-mvp` from the bootstrap `main` branch.
- [ ] Publish one intentional implementation commit.
- [ ] Open a draft pull request.
- [ ] Inspect GitHub Actions status.
- [ ] Do not merge automatically.
