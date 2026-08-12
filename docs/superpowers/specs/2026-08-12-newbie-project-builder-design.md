# Newbie Project Builder Design Specification

**Status:** Implemented MVP design
**Date:** August 12, 2026

## Goal

Create a shareable Windows and Linux project-builder that a person with no computer
experience can run safely, while preserving expert-grade logs, tests, security boundaries,
and GitHub workflows.

## Users

- Complete beginners creating their first GitHub project.
- Instructors or team leads sharing a repeatable setup.
- Technical support personnel diagnosing beginner setup failures.

## Required user experience

- Windows starts by double-clicking one file.
- Supported Linux starts with `bash start-linux.sh`.
- The main interface uses numbered choices and ordinary language.
- Every change explains what, why, affected resources, success, failure, and recovery.
- A preview mode performs no commands and writes no project files.

## Supported platforms

- Windows 10 and 11.
- Ubuntu, Debian, and Kali Linux through APT.
- Python 3.11, 3.12, and 3.13.

Unsupported systems receive diagnostics and manual guidance rather than guessed installation
commands.

## Architecture

Use two thin native launchers and one shared dependency-light Python core. Separate host
identification, preflight checks, command execution, logging, installation plans, project
generation, GitHub operations, AI integrations, state, backups, and support archives through
focused modules.

## Functional requirements

1. Detect the operating system and supported package manager.
2. Check disk space, GitHub reachability, and required/recommended tools.
3. Offer exact WinGet or APT plans and require confirmation.
4. Generate verbose redacted logs with stable operation IDs.
5. Present stable `NPB-###` errors with plain recovery guidance.
6. Store resumable workflow state.
7. Generate a conservative repository scaffold from a beginner questionnaire.
8. Refuse nonempty destinations by default and back up approved replacements.
9. Initialize local Git and optionally create the first checkpoint.
10. Authenticate to GitHub through the official browser flow without collecting tokens.
11. Confirm repository visibility, creation, and initial publication separately.
12. Refuse feature publication from `main` and never force-push.
13. Provide Superpowers verification guidance and optional Agency Agents core installation.
14. Create a sanitized support archive containing only allowlisted builder diagnostics.
15. Remove only marked builder-owned data during cleanup.

## Project templates

- `python-cli`: runnable source, tests, CI, checks, docs, and policies.
- `generic`, `web-app`, `web-api`, `desktop-app`, `ai-app`: planning-first scaffolds.
- `authorized-security-tool`: planning-first scaffold plus authorization, allowlist, denylist,
  prohibited action, evidence, and cleanup documentation.

## Security requirements

- No credential input or storage.
- Redact before persistence.
- No hidden raw logs.
- No shell interpolation for variable command arguments.
- Exact Windows package IDs.
- Explicit distribution allowlist for automatic Linux installation.
- Human confirmation for system install, remote creation, public visibility, and push.
- No merge, release, deployment, force-push, or security bypass.
- Cleanup marker and path-containment validation.

## Testing requirements

- Branch-aware coverage gate of at least 95%.
- Tests for redaction, dry-run, command logs, state, backups, name validation, destination
  refusal, Git behavior, GitHub confirmation helpers, integration checks, support bundles,
  menus, and CLI behavior.
- CI on Windows and Linux for Python 3.11 through 3.13.
- Ruff, mypy, package build, Bandit, and pip-audit checks.

## Documentation requirements

- Root README.
- Separate Windows and Linux beginner guides.
- Error catalog and troubleshooting.
- Architecture and security model.
- Implementation status and roadmap.
- AI-integration guidance.
- Shareable Grandma Test.
- Contributor, security, pull-request, issue, and changelog files.

## Non-goals for version 0.1.0

- Graphical user interface.
- Signed installer.
- Automatic merge, release, deployment, or deletion.
- Framework-specific runnable code for every project category.
- Universal Linux package-manager support.
- Automatic GitHub ruleset or security-feature administration.

## Acceptance criteria

- A local Python CLI project can be previewed and generated.
- Dry-run does not create the destination.
- Tests pass with the configured coverage gate.
- CI covers supported Python and operating-system combinations.
- Sensitive sample values are absent from persisted logs and support archives.
- The beginner workflow never requires a token or permanent security-policy change.
