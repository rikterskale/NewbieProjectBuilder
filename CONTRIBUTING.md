# Contributing

## Before changing code

Open or select one small issue. Explain the user problem, expected result, non-goals, risks,
and how the change will be tested. Architectural changes require an approved specification
under `docs/superpowers/specs/` and an implementation plan under `docs/superpowers/plans/`.

## Local setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
```

Windows PowerShell activation:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Required checks

```bash
python -m pytest
python -m ruff check .
python -m mypy src
python -m bandit -r src
python -m pip_audit
python -m build
```

Add or update tests for behavior changes. Tests must demonstrate a meaningful failure before
the implementation change. Do not add text-presence tests merely to increase coverage.

## Pull requests

Use a feature branch. Keep the PR small. Include the reason, specification/plan links, exact
verification commands, security impact, documentation updates, known limitations, and
rollback. Open it as a draft until every required check passes.
