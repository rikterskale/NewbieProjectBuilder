# Implementation Status

**Version:** 0.1.0 alpha
**Reviewed:** August 12, 2026

## Implemented

### Cross-platform foundation

- Shared Python 3.11+ core with no runtime third-party dependencies.
- Windows double-click launcher.
- PowerShell bootstrap without permanent execution-policy changes.
- Ubuntu, Debian, and Kali Bash launcher.
- Read-only diagnostics for OS support, disk, network, and tools.

### Safety and recoverability

- Stable `NPB-###` beginner error cards.
- Dry-run command and project preview behavior.
- Verbose operation IDs and redacted technical logs.
- Redaction for common GitHub, bearer, AWS, assignment, URL-credential, and private-key
  patterns.
- Workflow state for interrupted operations.
- Backup-aware file replacement.
- Builder ownership marker and containment checks for cleanup.
- Sanitized support archives that exclude project source and general user documents.

### Project generation

- Portable project-name validation.
- Conservative nonempty-folder refusal.
- Generic planning-first template.
- Runnable Python CLI template with source, tests, CI, and beginner documentation.
- Planning-first web, API, desktop, AI, and authorized-security templates.
- Authorization and scope document for security-tool projects.
- Optional local Git initialization and confirmed first checkpoint.

### GitHub boundary

- Browser-based GitHub CLI authentication.
- Active-account display before remote changes.
- Confirmed private/public repository creation.
- Typed confirmation before public visibility.
- Confirmed initial publication.
- Feature publication helper that refuses `main` and never force-pushes.

### AI workflow integration

- Codex status guidance.
- Superpowers plugin verification guidance.
- Optional installation of eight Agency Agents core roles.
- Explicit prevention of NEXUS or Agents Orchestrator becoming a competing controller.

### Quality system

- Unit and integration-style tests with a 95% branch-aware coverage gate.
- Windows and Linux CI matrix for Python 3.11, 3.12, and 3.13.
- Ruff, mypy, package-build, Bandit, and dependency-audit jobs.
- Pinned GitHub Actions and Dependabot configuration.

## Partially implemented

- Resume state is durable and inspectable, but not every interactive wizard branch yet offers
  a polished “continue from the last step” menu.
- Agency Agents can be installed through official scripts when Bash is available; the Windows
  desktop application remains the recommended fallback.
- Non-Python project choices receive complete planning scaffolds, not framework-specific
  runnable applications.

## Not implemented in version 0.1.0

- Signed Windows executable or installer.
- Graphical desktop wizard.
- Fedora, RHEL, Arch, macOS, or other package-manager automation.
- Automated repository ruleset, secret-scanning, or CodeQL configuration through GitHub API.
- Automatic pull-request creation from generated projects.
- Automatic release, deployment, merge, or destructive cleanup.
- In-application update installation.
- Cryptographic verification of downloaded third-party repositories.

## Local validation record

The implementation was compiled and tested in the build environment. The test configuration
requires 95% branch-aware coverage. Linting, typing, package, and security tools are also
required in GitHub Actions; their remote status is authoritative when local installation of
development dependencies is unavailable.
