# The Grandma Test

A release is not beginner-ready merely because an experienced developer can use it.

## Acceptance scenario

A person who has never used Git, GitHub, Python, PowerShell, Bash, or a terminal should be
able to:

1. Download the official release.
2. Start the Windows or supported Linux launcher.
3. Understand what the program will change.
4. Decline an operation without damage.
5. Run computer diagnostics.
6. Create a local private practice project.
7. Find the generated README and beginner guide.
8. Find the latest redacted log.
9. Create and inspect a sanitized support bundle.
10. Exit and rerun the builder safely.

They must not need to:

- Paste a token.
- Permanently change a security setting.
- Memorize a command.
- Interpret a Python traceback as the only explanation.
- Guess whether a project is public.
- Know the difference between `main`, a branch, a commit, and a pull request before the
  builder explains it.

## Observer checklist

- [ ] Every screen states what will happen next.
- [ ] Every change explains why it is needed.
- [ ] Confirmation text names the affected software, folder, repository, or branch.
- [ ] Cancel returns safely.
- [ ] Success is visible and specific.
- [ ] Failure provides an `NPB-###` code, plain explanation, fixes, and log location.
- [ ] The user can find all created files afterward.
- [ ] The user never handles a credential.
- [ ] Nothing is published, deleted, merged, released, or deployed unexpectedly.
- [ ] A second beginner can repeat the process from the written guide alone.

## Printable emergency card

```text
STOP if you see a password, token, private key, or request to disable security.

1. Do not paste the secret.
2. Do not force-push or delete files.
3. Write down the NPB error code.
4. Open the latest log from the builder menu.
5. Create a sanitized support bundle.
6. Review the bundle before sharing it.
7. When a real credential was exposed, revoke or rotate it first.
```
