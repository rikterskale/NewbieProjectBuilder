# Security Policy

## Report privately

Do not open a public issue containing:

- Passwords, tokens, cookies, API keys, or private keys.
- Personal or company-private information.
- Unsanitized logs or support bundles.
- Active exploit instructions that would put users at risk.

Use GitHub private vulnerability reporting when it is available. Otherwise contact the
repository owner through a trusted private channel.

## Security design

Newbie Project Builder is an installer and project generator, so it follows a stricter model
than an ordinary documentation repository:

- No token input fields.
- Browser-based GitHub CLI authentication.
- Explicit argument lists instead of shell-generated command strings.
- Exact WinGet package IDs.
- APT support limited to identified distributions.
- Confirmation before system installation, repository creation, public visibility, and push.
- Typed confirmation for public repositories and cleanup.
- Redaction before persistence.
- No hidden unredacted log.
- Support bundles exclude project and user files.
- Cleanup requires a builder ownership marker and path-containment validation.
- No force pushes, merges, releases, or deployments.

## Supported versions

Until version 1.0, only the newest released version receives security fixes.

## What to include

- Affected version or commit.
- Operating system.
- Plain-language impact.
- Safe reproduction steps.
- Sanitized evidence.
- Suggested mitigation, when known.

## Secret exposure

When a real credential appears in a log, issue, commit, or screenshot:

1. Stop using it.
2. Revoke or rotate it immediately.
3. Remove it from current files.
4. Remove it from Git history through an approved process when necessary.
5. Re-run secret scanning.
6. Document the incident without reproducing the secret.
