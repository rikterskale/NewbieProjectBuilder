# Start Here on Ubuntu, Debian, or Kali Linux

This guide assumes no Linux command-line experience. The automated installer supports
APT-based Ubuntu, Debian, and Kali Linux in the first release.

## Before you begin

You need:

- A supported Linux distribution.
- An internet connection for software downloads and GitHub access.
- At least 2 GB of free disk space.
- Your own account password when `sudo` is needed for package installation.
- A GitHub account for online repositories.

The builder never reads or stores the password entered into `sudo`.

## Download and open the repository

Download the repository ZIP from:

```text
https://github.com/rikterskale/NewbieProjectBuilder
```

Extract it, open the resulting folder in the Files application, right-click an empty area, and
choose **Open in Terminal**.

## Start the program

Copy and paste:

```bash
bash start-linux.sh
```

Using `bash` directly means you do not need to change file permissions first.

## What the launcher checks

The launcher looks for Python 3.11 or newer. When it is missing and APT is available, it can
offer to run:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git curl ca-certificates
```

The complete command appears before execution. Type `YES` only when you intend to install
those packages. `sudo` may ask for your Linux account password; the characters normally do
not appear while you type.

When APT is unavailable, the script stops with `NPB-011` instead of guessing commands for an
unsupported distribution.

## Main menu

The Windows and Linux menus are the same because both launchers use the shared Python core.
Enter a displayed number. Invalid input simply repeats the menu.

## Create a project

Choose **Create a new project**. The default parent folder is:

```text
~/GitHub-Projects
```

The builder rejects a nonempty destination by default. It will not silently replace an
existing project.

The first release provides runnable application code for the Python CLI template. Other
project types receive a planning-first structure so an AI agent does not choose an
unapproved framework.

## Git and GitHub

The builder can initialize the local repository and create an initial commit. When Git needs
an identity, the name and email are saved only in that project.

GitHub CLI uses browser authentication:

```text
gh auth login --web --git-protocol https
```

You should not paste a personal access token into the builder. Confirm the displayed GitHub
account before approving repository creation.

Public repositories require the exact phrase `MAKE PUBLIC`.

## Logs and support bundles

Logs are stored under:

```text
~/NewbieProjectBuilder/logs
```

Support bundles are stored under:

```text
~/NewbieProjectBuilder/support
```

The bundle includes sanitized logs and system metadata. It excludes project source, normal
user documents, browser data, environment variables, and credentials.

## Common Linux issues

### `python3: command not found`

Run `bash start-linux.sh` again and approve the supported APT installation. Do not download a
random Python installer from an advertisement or unofficial page.

### `sudo: command not found`

The environment may be a restricted container or unusual distribution. Automatic package
installation is not supported there. Run diagnostics only and ask the system administrator.

### `Unable to locate package gh`

The distribution's configured repositories may not contain GitHub CLI. The local project can
still be created. Install GitHub CLI using GitHub's official distribution-specific
instructions, then run diagnostics again.

### Permission denied

Do not solve project-folder permission errors with broad commands such as `chmod -R 777`.
Check folder ownership and select a folder under your own home directory.

### The browser does not open for GitHub sign-in

GitHub CLI normally prints a one-time code and URL. Open the URL manually in your browser,
enter the displayed code, and confirm the correct account.

## Unsupported distributions

Fedora, RHEL, Arch, openSUSE, and other distributions are not automatically modified in the
first release. The builder should report `NPB-001` or `NPB-011` and offer diagnostic/manual
instructions. Do not substitute an APT command on a non-APT distribution.
