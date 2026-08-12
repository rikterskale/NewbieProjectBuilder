# Newbie Project Builder Agent Rules

## Primary user

Assume the user may never have used GitHub, Git, a terminal, PowerShell, Bash, Python, or a
package manager. Every user-facing change must remain understandable without prior computer
knowledge.

## Required explanation pattern

For each operation, explain:

1. What will happen.
2. Why it is needed.
3. What files, settings, software, or remote resources may change.
4. Whether administrator access may be requested.
5. What success looks like.
6. Where the full redacted log is stored.
7. What the user should do when it fails.

## Safety invariants

- Never collect credentials.
- Never print or persist a known secret.
- Never create a hidden unredacted log.
- Never use shell interpolation for variable command arguments.
- Never use force push.
- Never merge, release, deploy, or make a repository public without explicit confirmation.
- Never delete a generated project during builder cleanup.
- Never recursively delete outside a marked builder-owned directory.
- Never silently replace an existing project file.
- Never permanently weaken operating-system, antivirus, browser, Codex, or GitHub security policy.
- A process-scoped PowerShell execution setting is allowed only for the documented launcher; never alter the user or machine policy.
- Never weaken CI merely to make it pass.

## Development workflow

1. Read the approved specification and implementation plan.
2. Work on a feature branch or isolated worktree, not `main`.
3. Write a failing behavioral test.
4. Confirm the expected failure.
5. Add the minimum implementation.
6. Run focused tests, then the full suite.
7. Run linting, type checking, security checks, and packaging checks.
8. Update Windows and Linux beginner documentation.
9. Review the final diff for unrelated files and credentials.
10. Open a draft pull request; do not merge automatically.

## Logging

Every external command records timestamp, operation ID, step, working directory, redacted
arguments, duration, exit code, stdout, stderr, and result. Redaction occurs before writing.
Tests must prove representative credentials cannot reach logs or support bundles.

## Error handling

Use stable `NPB-###` codes. An error card must explain the problem in ordinary language,
state that no additional action was attempted, provide safe recovery steps, and identify the
log path. Do not expose stack traces as the only user-facing explanation.

## Platform rules

- Windows and Linux launchers remain thin.
- Shared behavior lives in the Python package.
- Windows package installation uses exact WinGet IDs.
- Linux automatic installation is limited to explicitly supported APT distributions.
- Unsupported systems receive diagnostic/manual guidance, not guessed commands.
- Never require a permanent PowerShell execution-policy change.

## Documentation gates

Update documentation when installation, prompts, menu choices, commands, file locations,
platform support, generated files, safety behavior, errors, or limitations change. Maintain:

- `README.md`
- `docs/START_HERE_WINDOWS.md`
- `docs/START_HERE_LINUX.md`
- `docs/TROUBLESHOOTING.md`
- `docs/ERROR_CODES.md`
- `docs/IMPLEMENTATION_STATUS.md`
- `CHANGELOG.md`
