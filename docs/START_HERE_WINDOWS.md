# Start Here on Windows

This guide assumes you have no computer experience. You do not need to know Git, Python,
PowerShell, or command-line syntax to use the normal setup path.

## Before you begin

You need:

- A Windows 10 or Windows 11 computer.
- An internet connection for downloading software and connecting to GitHub.
- A GitHub account when you want an online repository.
- Permission to install software on the computer.
- At least 2 GB of free disk space.

Never paste a password, GitHub token, API key, private key, or company secret into the
builder, a GitHub issue, or a support message.

## Download the builder safely

Use only the official repository:

```text
https://github.com/rikterskale/NewbieProjectBuilder
```

On GitHub, choose **Code**, then **Download ZIP**. After the download finishes:

1. Open the Downloads folder.
2. Right-click the ZIP file.
3. Choose **Extract All**.
4. Accept the proposed destination.
5. Open the extracted `NewbieProjectBuilder` folder.

A future signed installer may replace these steps. Until then, the source launchers keep the
process visible and auditable.

## Start the program

Double-click:

```text
START-WINDOWS.cmd
```

A black or blue terminal window opens. This is normal. The first screen explains that the
program will not publish or delete anything without permission. It also shows the bootstrap
log location.

The `.cmd` file starts `Start-Windows.ps1` with a PowerShell execution-policy bypass that
applies only to that one process. It does not permanently change the computer's policy.

## When Python is missing

The launcher checks for Python 3.11 or newer. When it cannot find Python, it checks for
Windows Package Manager, also called WinGet.

It displays the exact proposed package:

```text
Python.Python.3.12
```

Type `YES` only when you intend to install Python. WinGet may open an administrator prompt.
Read the prompt and verify that it refers to Python before approving it.

After installation, close the window and double-click `START-WINDOWS.cmd` again. Windows
sometimes needs a new process before an installed program appears in PATH.

## Main menu

Enter the number beside the action you want:

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

Typing a different value does not run anything. The menu asks again.

## First-time computer setup

Choose **1**. The builder checks:

- Windows version and processor type.
- Free disk space.
- Basic access to GitHub over HTTPS.
- Python.
- Git.
- GitHub CLI.
- Codex CLI.
- Bash.
- WinGet.
- GitHub Desktop.

The screen uses three markers:

```text
[PASS] The item is available.
[WARN] The item is optional but missing or unavailable.
[FIX ] A required item needs attention.
```

When Git, GitHub CLI, or GitHub Desktop is missing, the builder shows the exact WinGet
command before asking permission. Answering **No** skips that installation.

The builder never asks for a GitHub token. GitHub CLI authentication uses the browser.

## Create a new project

Choose **2** and answer the questions.

### Project name

Use an ordinary name such as:

```text
Weather Helper
Family Recipe Organizer
Simple Inventory Tool
```

The builder creates a portable folder name such as `weather-helper`. Reserved Windows names
such as `CON`, `AUX`, or `LPT1` are rejected.

### Project type

The working code template in the first release is **Python command-line tool**. The other
choices create a complete planning and GitHub structure but deliberately wait for an
approved architecture before generating application code.

### Who will use it?

Examples:

```text
Only me
My family
My work team
The public
```

### Repository location

Choose private unless you have a clear reason to make the project public. A private
repository is visible only to you and people you invite.

A public repository can expose every committed file to the world. Public creation therefore
requires typing:

```text
MAKE PUBLIC
```

### Parent folder

The default is:

```text
Documents\GitHub-Projects
```

Press Enter to accept it.

### Final preview

The builder shows the project name, folder, type, visibility, and number of files. Nothing has
been created yet. To continue, type:

```text
CREATE PROJECT
```

Any other text cancels the operation.

## First local Git checkpoint

When Git is available, the builder can create a local repository. It then offers to make the
first checkpoint, called a commit.

A commit is a saved description of the current files. The builder uses:

```text
chore: initialize project
```

When Git does not know your name or email, the builder asks for them and saves them only in
that project. It does not silently change the global Git identity for every repository.

## GitHub sign-in and repository creation

When you selected private or public GitHub visibility, the builder checks GitHub CLI.

If sign-in is required, approve browser sign-in. Confirm the GitHub account displayed by the
builder before repository creation. The program then shows:

- Account.
- Repository name.
- Visibility.

Repository creation and initial publishing are separate questions. Saying **No** leaves the
project local and safe.

## GitHub Desktop after creation

Open GitHub Desktop and choose:

1. **File**.
2. **Add local repository**.
3. **Choose**.
4. Select the new project folder.
5. Confirm that the current branch is `main`.

For a new feature, create a branch such as `feature/add-search`. Do not implement unfinished
work directly on `main`.

## Logs

The default log folder is:

```text
Documents\NewbieProjectBuilder\logs
```

Each operation has an ID such as:

```text
NPB-20260812-153000-A1B2
```

The log contains commands, output, errors, exit codes, and durations. Credential-like values
are redacted before writing.

## Create a safe support bundle

Choose menu item **7**. The program creates a ZIP under:

```text
Documents\NewbieProjectBuilder\support
```

It excludes project source and ordinary personal documents. Open the ZIP and review it before
sharing it.

## Cleanup

Menu item **8** removes only builder-owned state, logs, support bundles, backups, and the
builder-owned Agency checkout. It requires the exact phrase:

```text
DELETE BUILDER DATA
```

The builder verifies its ownership marker and checks that every deletion path remains inside
the builder folder. Generated projects are not included.

## Stop immediately when

- A prompt asks for a token or password outside a normal Windows administrator or browser
  sign-in screen.
- A download did not come from the official repository or official package source.
- The displayed GitHub account is not yours.
- A public repository was selected accidentally.
- A security product warns that a file differs from the documented release.
- You do not understand a destructive or publishing action.

Choose **No** or close the window. Closing the builder does not delete the project.
