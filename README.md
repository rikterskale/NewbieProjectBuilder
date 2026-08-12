# Newbie Project Builder

A safety-first Windows and Linux setup wizard for people who may have never used Git,
GitHub, a terminal, or a coding tool.

The beginner experience is intentionally simple:

```text
Windows: Double-click START-WINDOWS.cmd

Ubuntu, Debian, or Kali Linux:
bash start-linux.sh
```

The launchers start one shared Python core, so Windows and Linux use the same project
rules, error explanations, redaction, logging, templates, and tests.

## What the builder does

Newbie Project Builder can:

- Detect Windows, Ubuntu, Debian, and Kali Linux.
- Check Python, Git, GitHub CLI, Codex CLI, Bash, WinGet, APT, and GitHub Desktop.
- Report free disk space and basic GitHub network reachability.
- Offer exact package-manager commands before executing them.
- Create a complete beginner-oriented repository scaffold.
- Create a working Python CLI starter with tests and CI.
- Create planning-first scaffolds for web, API, desktop, AI, and authorized-security projects.
- Initialize a local Git repository.
- Optionally create the first local commit using project-only Git identity settings.
- Use browser-based GitHub CLI authentication without collecting tokens.
- Create private or public repositories only after explicit confirmation.
- Require a second typed confirmation before public repository creation.
- Install a small Agency Agents core roster when Bash and Codex integration are available.
- Show guidance for verifying the Superpowers plugin in Codex.
- Create verbose redacted logs and sanitized support archives.
- Resume interrupted setup workflows from a small state file.
- Remove builder-owned logs, backups, state, support archives, and integration checkouts
  without touching generated projects.

## Safety guarantees

The program is designed around these rules:

1. **No secret collection.** It never asks you to paste a GitHub token, API key, password,
   private key, or cookie.
2. **No silent publishing.** Repository creation and initial publishing require visible
   confirmation.
3. **No automatic merge or release.** The builder does not merge pull requests, publish
   releases, or deploy projects.
4. **No force pushes.** Feature publishing refuses to push directly from `main`.
5. **No silent overwrite.** A nonempty project folder is rejected by default. Approved
   replacements are backed up first.
6. **No hidden raw logs.** Credentials are redacted before logs are written; there is no
   second unredacted log.
7. **No project deletion during cleanup.** Cleanup operates only under the marked builder
   data folder and excludes generated projects.
8. **No security-control bypass.** The launchers do not permanently disable PowerShell,
   SmartScreen, antivirus, workspace policy, CI, or branch protections.

## Windows quick start

1. Download or clone this repository from the official GitHub page.
2. Open the `NewbieProjectBuilder` folder in File Explorer.
3. Double-click `START-WINDOWS.cmd`.
4. Read the first screen and press the requested key.
5. Approve only software you recognize and intended to install.
6. Choose **Create a new project** from the menu.

The Windows launcher uses PowerShell only for the current process. It checks for Python
and can offer the exact WinGet package `Python.Python.3.12` when Python is missing.

Detailed instructions: [`docs/START_HERE_WINDOWS.md`](docs/START_HERE_WINDOWS.md)

## Linux quick start

The automated Linux path supports Ubuntu, Debian, and Kali Linux.

Open a terminal in this folder and run:

```bash
bash start-linux.sh
```

No `chmod` command is required for that beginner path. When Python is missing, the script
can offer an APT installation of Python, Git, and basic certificate/network packages.
`sudo` receives the password directly; the builder does not read or store it.

Detailed instructions: [`docs/START_HERE_LINUX.md`](docs/START_HERE_LINUX.md)

## Main menu

```text
1. Set up this computer
2. Create a new project
3. Check or diagnose the computer
4. Show AI integration status
5. Install the Agency Agents core roster
6. Open the latest log location
7. Create a sanitized support bundle
8. Remove builder-owned data
9. Exit
```

## Preview mode

Preview mode records what would happen but does not execute package-manager, Git, or
GitHub commands and does not create project files.

Windows PowerShell:

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m newbie_project_builder --dry-run create `
  --name "Weather Helper" `
  --kind python-cli `
  --visibility local-only `
  --parent "$HOME\Documents\GitHub-Projects"
```

Linux:

```bash
PYTHONPATH=src python3 -m newbie_project_builder --dry-run create \
  --name "Weather Helper" \
  --kind python-cli \
  --visibility local-only \
  --parent "$HOME/GitHub-Projects"
```

## Noninteractive project creation

This is intended for administrators, testing, and repeatable labs. It creates local files
only; it does not create or publish a GitHub repository.

```bash
PYTHONPATH=src python3 -m newbie_project_builder create \
  --name "Example Tool" \
  --kind python-cli \
  --audience "My team" \
  --visibility local-only \
  --parent "$HOME/GitHub-Projects"
```

Available project kinds:

- `generic`
- `python-cli`
- `web-app`
- `web-api`
- `desktop-app`
- `ai-app`
- `authorized-security-tool`

The first release generates runnable application code only for `python-cli`. Other choices
receive a complete planning, documentation, GitHub, security, and CI structure. This is
deliberate: the builder does not silently select a web, desktop, AI, or security framework
before the owner approves an architecture.

## Logs

Beginner screens show compact results such as:

```text
[PASS] Git: Installed at /usr/bin/git
[WARN] Codex CLI: Installed at <not found>
[FIX ] Free disk space: 0.45 GB free
```

Technical logs include:

- Timestamp.
- Operation ID.
- Step name.
- Working directory.
- Redacted command.
- Duration.
- Exit code.
- Standard output.
- Error output.
- PASS, FAIL, SKIPPED, or DRY-RUN status.

Default log locations:

```text
Windows: Documents\NewbieProjectBuilder\logs\
Linux:   ~/NewbieProjectBuilder/logs/
```

The redactor covers common GitHub tokens, GitHub fine-grained token prefixes, bearer
tokens, AWS access-key patterns, password/token/secret assignments, URL credentials, and
private-key blocks.

## Support bundles

The support-bundle menu creates a ZIP file containing only:

- A small system-information JSON document.
- Up to five recent sanitized logs.
- Sanitized builder workflow state, when present.
- A README explaining what is included.

It excludes project source, user documents, browser data, environment variables, and
credentials. Review the ZIP before sharing it.

## Agency Agents and Superpowers

The intended division of responsibility is:

> Superpowers controls the development workflow. Agency Agents supplies the smallest set
> of specialists required for the current task. The project owner approves external side
> effects and merges.

The optional Agency installation selects only:

- Product Manager
- Software Architect
- Code Reviewer
- Test Automation Engineer
- AppSec Engineer
- DevOps Automator
- Technical Writer
- Reality Checker

It does not intentionally activate NEXUS or Agents Orchestrator. On Windows, the official
Agency Agents desktop application remains the recommended fallback when Bash-based
repository scripts are unavailable.

Superpowers verification remains a guided Codex step because plugin availability can be
controlled by the Codex installation, account, and workspace policy.

## Development checks

The repository requires Python 3.11 or newer.

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m mypy src
python -m bandit -r src -ll
python -m pip_audit
```

The test configuration enforces branch-aware coverage of at least 95 percent. The initial
implementation currently has 64 passing tests and 96.27 percent measured branch-aware
coverage in the local validation environment.

## Project status

This is a working Phase 1–3 MVP:

- Phase 1: prerequisite diagnostics, installers, logging, redaction, state, error handling.
- Phase 2: project questionnaire, scaffolding, backups, Git initialization.
- Phase 3: browser-based GitHub authentication, repository creation, initial publishing.
- Phase 4 foundation: Codex/Superpowers status guidance and Agency core installation.

A signed graphical installer, more project templates, repository-ruleset automation, and
full clean-machine release testing remain roadmap items.

See [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md) and
[`docs/ROADMAP.md`](docs/ROADMAP.md).

## Documentation map

| Document | What it explains |
|---|---|
| [`docs/START_HERE_WINDOWS.md`](docs/START_HERE_WINDOWS.md) | Click-by-click Windows setup and recovery |
| [`docs/START_HERE_LINUX.md`](docs/START_HERE_LINUX.md) | Ubuntu, Debian, and Kali setup and recovery |
| [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) | Common failures and safe fixes |
| [`docs/ERROR_CODES.md`](docs/ERROR_CODES.md) | Stable `NPB-###` error meanings |
| [`docs/GRANDMA_TEST.md`](docs/GRANDMA_TEST.md) | Acceptance criteria for a person with no computer experience |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Components, boundaries, and data flow |
| [`docs/SECURITY_MODEL.md`](docs/SECURITY_MODEL.md) | Threat model, trust boundaries, and safety invariants |
| [`docs/AI_INTEGRATIONS.md`](docs/AI_INTEGRATIONS.md) | Superpowers and Agency Agents operating model |
| [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md) | Implemented versus planned capabilities |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Later phases and release work |

## One-command maintainer checks

After installing the development dependencies, run the platform-appropriate wrapper:

```powershell
.\scripts\check.ps1
```

```bash
bash scripts/check.sh
```

These wrappers compile the package, run Ruff, mypy, tests and coverage, Bandit, the
installed-dependency audit, and the package build. They stop at the first failed gate and
return a nonzero exit code.

## Security

Read [`SECURITY.md`](SECURITY.md) before reporting a vulnerability. Never put credentials,
private data, or active exploit details in a public issue.

## License

MIT License. See [`LICENSE`](LICENSE).
