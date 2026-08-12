# Architecture

## Purpose

Newbie Project Builder provides a safe, understandable setup and repository-generation
workflow for people with little or no computer experience. It separates operating-system
bootstrap work from shared application behavior so Windows and Linux do not become two
independent products.

## System context

```text
Beginner
   |
   +--> START-WINDOWS.cmd --> Start-Windows.ps1 --+
   |                                               |
   +--> bash start-linux.sh -----------------------+--> shared Python core
                                                        |
                                                        +--> diagnostics
                                                        +--> package plans
                                                        +--> project generator
                                                        +--> Git operations
                                                        +--> GitHub CLI boundary
                                                        +--> AI integration checks
                                                        +--> redacted logging
                                                        +--> support bundle
```

## Components

### Native launchers

The launchers perform only the minimum work needed to locate a compatible Python runtime,
show a beginner safety message, offer an approved prerequisite installation, and start the
Python package. They do not contain project-generation or GitHub business logic.

### Application controller

`app.py` controls menus and visible workflow transitions. It coordinates services but does
not implement subprocess execution, redaction, template rendering, or GitHub parsing itself.

### Host and preflight services

`host.py` identifies Windows or Linux and recognizes APT-based Ubuntu, Debian, and Kali.
`preflight.py` performs read-only checks for operating system support, disk space, network
reachability, and required or recommended tools.

### Command execution and technical logs

`commands.py` executes argument arrays without shell interpolation. `technical_logging.py`
records a timestamp, operation ID, working directory, redacted command, duration, exit code,
stdout, stderr, and result. `redaction.py` removes supported credential patterns before data
is persisted.

### Installation plans

`installer.py` builds explicit operating-system-specific installation plans. Windows plans
use exact WinGet identifiers. Linux plans are limited to recognized APT systems. The user
sees and confirms each plan before execution.

### Project generator

`project.py` validates portable names, previews output, refuses a nonempty destination by
default, creates backups before an approved replacement, writes templates, and optionally
initializes Git. Runnable application code is currently generated only for the Python CLI
template; other project types receive a planning-first structure to avoid unapproved
framework choices.

### Git and GitHub boundary

`github.py` uses the GitHub CLI only through the shared command runner. Authentication is
browser-based. Repository creation, public visibility, and initial publication require
visible confirmation in the application layer. Feature publication refuses the `main`
branch and never force-pushes.

### AI integration boundary

`integrations.py` reports Codex and Superpowers guidance and can install a deliberately small
Agency Agents roster. Superpowers remains the workflow controller; Agency Agents provides
specialist roles only.

### Recovery and support

`state.py` stores resumable workflow progress. `backup.py` preserves files before approved
replacement. `support.py` packages a small sanitized diagnostic archive and excludes project
source and general user documents.

## Data flow

1. The launcher establishes the builder-owned home folder and starts Python.
2. `Paths.ensure()` creates marked builder-owned log, state, backup, support, and integration
   locations.
3. The application performs a read-only preflight before offering changes.
4. Every external command flows through `CommandRunner` and the redacted operation log.
5. Project input is converted to a validated `ProjectOptions` object.
6. Template content is previewed before generation.
7. Local Git and remote GitHub actions occur only after separate confirmation gates.

## Dependency policy

The runtime has no third-party Python dependencies. Development-only tools provide testing,
coverage, linting, typing, packaging, dependency auditing, and static security analysis.
This keeps first-run behavior understandable and reduces supply-chain exposure.

## Design trade-offs

- A console wizard is less visually polished than a graphical installer but is easier to
  audit, test, and repair during the MVP stage.
- Supporting only APT-based Linux distributions initially is safer than guessing package
  commands across every distribution.
- Planning-first templates provide less instant code for web, desktop, AI, and security
  projects but avoid silently selecting a framework the owner did not approve.
- GitHub CLI is an external prerequisite, but it provides browser authentication without
  asking the builder to handle personal access tokens.

## Extension rules

New integrations must:

- Use typed interfaces and argument arrays.
- Declare permissions and remote side effects.
- Provide dry-run behavior.
- Add stable beginner error handling.
- Add secret-redaction tests when new output may contain sensitive data.
- Update both Windows and Linux documentation.
- Preserve the human gates for publish, merge, release, deploy, delete, and security-sensitive
  actions.
