# Troubleshooting

## The program window closes immediately on Windows

Open the extracted folder and double-click `START-WINDOWS.cmd`, not the PowerShell file. The
CMD wrapper pauses before closing and displays the exit code. Check:

```text
Documents\NewbieProjectBuilder\logs
```

## PowerShell says running scripts is disabled

Use `START-WINDOWS.cmd`. It launches the PowerShell script with a process-only execution
policy. Do not permanently set the machine policy to unrestricted.

## WinGet is not recognized

Install or update **App Installer** from Microsoft Store. Restart Windows or open a new
terminal. Run the builder again.

## Python was installed but is still missing

Close every builder or terminal window and start again. PATH changes commonly require a new
process. When the problem remains, restart the computer and run diagnostics.

## Git is not recognized

Use first-time setup to install exact package `Git.Git`, then restart the builder. Do not
manually copy `git.exe` into random folders.

## GitHub sign-in fails

1. Confirm the internet connection.
2. Check whether a corporate proxy or VPN blocks GitHub.
3. Run diagnostics.
4. Use browser sign-in again.
5. Confirm the active account before repository creation.

Never solve authentication failures by posting a token in an issue or chat.

## The wrong GitHub account appears

Cancel repository creation. Use GitHub CLI account switching or sign out, then run diagnostics
again. Do not create the repository under the wrong personal or company account.

## The project folder already exists

`NPB-401` means the builder found existing files and refused to overwrite them. Choose a new
name, move the old folder after reviewing it, or use an advanced approved replacement flow
that creates backups first.

## Initial Git commit fails

The log usually identifies missing identity, permissions, or an unsupported repository state.
The builder can save a name and email only in the new project. Check that the project folder
is writable and that no antivirus product quarantined Git files.

## Push is rejected

Do not use `--force`. The remote may contain newer work or protection rules. Open GitHub
Desktop, choose **Fetch origin**, inspect incoming changes, and resolve the root cause.

## Tests fail

Use the systematic sequence:

1. Read the first failure and complete traceback.
2. Reproduce the same failure.
3. Inspect recent changes.
4. Find a similar working pattern.
5. State one root-cause hypothesis.
6. Test the smallest change.
7. Add or confirm a regression test.
8. Run focused and complete tests.

Do not delete, skip, or loosen a test solely to make CI green.

## Local tests pass but GitHub Actions fails

Compare:

- Operating system.
- Python version.
- Dependency versions and lock state.
- Filename capitalization.
- Line endings.
- Environment variables.
- File permissions.
- Test order and shared state.
- Network dependencies.

The first failing GitHub Actions step is more useful than the final red summary.

## Agency Agents installation fails

The optional repository installer requires Git and Bash. On Windows, the official Agency
Agents desktop application is the recommended fallback. Check that the cloned repository is
under the builder-owned integrations directory and read the `convert.sh` or `install.sh`
error in the log.

## Superpowers is not detected

Filesystem detection is best-effort. Open Codex, choose Plugins, search for Superpowers, and
verify it in a fresh session. Workspace policy may require an administrator.

## A support log contains a real secret

1. Stop sharing it.
2. Rotate the credential immediately.
3. Delete exposed copies.
4. Report the redaction gap privately.
5. Keep a sanitized reproduction that does not include the original value.
