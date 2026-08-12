# Security Model

## Assets protected

- GitHub credentials and authenticated sessions.
- API keys, passwords, cookies, private keys, and environment secrets.
- Existing project files and uncommitted work.
- The trusted `main` branch.
- Private repository content and private company information.
- User documents outside the builder-owned data folder.
- Operating-system security settings.

## Trust boundaries

```text
User input
   |
   v
Builder validation and confirmation
   |
   +--> local filesystem
   +--> subprocess tools (Git, gh, WinGet, APT)
   +--> GitHub remote resources
   +--> downloaded Agency Agents repository
```

Every boundary is treated as fallible. Tool output is logged only after redaction, file
operations are constrained to validated destinations, and remote changes require explicit
confirmation.

## Security invariants

1. The builder never asks for a token, password, private key, cookie, or API key.
2. Authentication uses the official GitHub CLI browser flow.
3. Commands are executed as argument arrays, not interpolated shell strings.
4. Logs are redacted before writing; no hidden raw log is retained.
5. Existing nonempty project folders are rejected unless replacement is explicitly selected.
6. Approved replacement creates a backup first.
7. Cleanup requires the builder ownership marker and path containment.
8. Feature publication refuses `main` and never force-pushes.
9. The builder does not merge, release, deploy, or bypass CI or branch protections.
10. Public repository creation requires an additional typed confirmation.
11. Automatic Linux installation is limited to identified APT systems.
12. Windows package installation uses exact WinGet package identifiers.

## Threats and controls

| Threat | Control |
|---|---|
| Credential appears in command output | Redact supported patterns before persistence and before support-bundle creation |
| Command injection through project input | Use subprocess argument arrays and validate names |
| Overwriting an existing project | Reject nonempty destination by default; backup before approved replacement |
| Accidental publication | Local-only default plus separate repository and push confirmations |
| Accidental public exposure | Private recommended; typed `MAKE PUBLIC` confirmation |
| Direct feature push to `main` | Branch check in GitHub helper; no force-push path |
| Cleanup deletes unrelated files | Marker file, containment check, and builder-data-only deletion |
| Malicious or compromised dependency | Dependency-light runtime, pinned CI actions, Dependabot, pip-audit, Bandit |
| Unsupported Linux command damages system | Stop on unrecognized distribution/package manager |
| Sensitive support bundle | Allowlisted contents, second redaction pass, documented review requirement |
| AI specialist overrides safe workflow | Repository instructions make Superpowers controller and external actions human-gated |

## Known limitations

- Pattern redaction reduces risk but cannot mathematically identify every possible secret.
  Users must review support archives before sharing.
- The MVP trusts official system package managers, Git, GitHub CLI, Codex, and the official
  Agency Agents repository once the user approves their use.
- Download signature verification and a signed graphical installer are not yet implemented.
- GitHub repository ruleset automation is not yet implemented.
- Clean-machine installation validation is performed by CI and planned VM acceptance tests;
  it is not a replacement for release signing.

## Security testing requirements

Every release must include:

- Representative token and private-key redaction tests.
- Tests proving dry-run does not execute commands or write projects.
- Tests proving public creation requires the typed phrase.
- Tests proving feature push refuses `main`.
- Tests proving cleanup rejects missing markers and unsafe paths.
- Static analysis with Bandit.
- Dependency audit with pip-audit.
- Cross-platform tests on Windows and Linux.

## Incident response

When a real credential is exposed, rotate or revoke it first. Removing a file or log alone
does not make an active credential safe. Preserve sanitized evidence, remove the value from
current content and Git history when required, then rerun security checks.
