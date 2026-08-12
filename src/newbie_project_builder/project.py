"""Deterministic, backup-aware project scaffold generation."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

from newbie_project_builder.backup import Backups
from newbie_project_builder.commands import Runner
from newbie_project_builder.errors import BuilderError
from newbie_project_builder.models import Paths, ProjectKind, ProjectOptions
from newbie_project_builder.redaction import contains_sensitive
from newbie_project_builder.technical_logging import OperationLog

_RESERVED = frozenset(
    {
        "aux",
        "con",
        "nul",
        "prn",
        *(f"com{number}" for number in range(1, 10)),
        *(f"lpt{number}" for number in range(1, 10)),
    }
)


@dataclass(frozen=True, slots=True)
class Generation:
    destination: Path
    created: tuple[Path, ...]
    backups: tuple[Path, ...]
    git_initialized: bool
    dry_run: bool


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)[:80].rstrip("-")
    if not slug or slug in _RESERVED:
        raise BuilderError("NPB-402", name)
    return slug


def _common(options: ProjectOptions) -> dict[str, str]:
    title = options.name
    description = options.description or f"A beginner-created {options.kind.value} project."
    files = {
        "README.md": dedent(
            f"""\
            # {title}

            {description}

            ## Start here

            - Windows: `docs/START_HERE_WINDOWS.md`
            - Linux: `docs/START_HERE_LINUX.md`
            - Purpose and boundaries: `docs/PROJECT_CHARTER.md`
            - AI workflow rules: `AGENTS.md` and `docs/AI_TOOLING.md`

            ## Safe workflow

            1. Define one small user problem.
            2. Approve the design and implementation plan.
            3. Work on a feature branch, never directly on `main`.
            4. Write a failing test before production code.
            5. Run the local check script.
            6. Open a pull request and merge only after evidence-based review.

            ## First-time development setup

            Windows PowerShell:

            ```powershell
            .\\scripts\\setup.ps1
            ```

            Linux:

            ```bash
            bash scripts/setup.sh
            ```

            ## Checks

            Windows PowerShell:

            ```powershell
            .\\scripts\\check.ps1
            ```

            Linux:

            ```bash
            bash scripts/check.sh
            ```

            Never commit passwords, tokens, private keys, `.env` files, or real private data.
            """
        ),
        "AGENTS.md": dedent(
            """\
            # Project Agent Rules

            ## Audience

            Assume the owner may have no computer experience. Explain unfamiliar terms, give
            exact paths and commands, state expected output, show the log path, and never invent
            success results.

            ## Controller

            Superpowers is the only development workflow controller. Agency Agents are
            specialists. Do not activate NEXUS or Agents Orchestrator as a competing controller.

            ## Instruction priority

            1. Current owner instruction.
            2. Security, privacy, authorization, and destructive-action restrictions.
            3. `docs/PROJECT_CHARTER.md`.
            4. Approved design specification.
            5. Approved implementation plan.
            6. This file.
            7. Specialist preferences.

            ## Design before code

            New projects and architectural changes require context review, purpose, users,
            constraints, non-goals, measurable success, two or three approaches, explicit design
            approval, a written specification in `docs/superpowers/specs/`, written-spec approval,
            and a detailed plan in `docs/superpowers/plans/` before production code.

            ## Git safety

            - Never implement directly on `main`.
            - Never force-push, merge, publish, release, deploy, or delete without approval.
            - Show modified and untracked files before removing a worktree.
            - Never discard user files to make a command succeed.

            ## TDD and debugging

            Write one failing behavioral test, observe the expected failure, add the minimum code,
            run focused and broader tests, refactor while green, and commit the tested change.
            For failures, reproduce and identify root cause before editing. After three failed fix
            attempts, reassess the architecture.

            ## Logs and security

            Logs include timestamp, operation ID, working directory, redacted command, duration,
            exit code, stdout, stderr, and recovery steps. Never save a hidden unredacted copy.
            Never commit credentials or private data. Validate input and paths, use least privilege,
            audit dependencies, and never disable a security check merely to make CI green.

            ## Completion

            Re-read the charter, specification, and plan; run formatting, linting, type checks,
            tests, coverage, build, dependency audit, secret scan, and static analysis; inspect the
            final diff; and verify documentation before claiming completion.
            """
        ),
        "docs/PROJECT_CHARTER.md": dedent(
            f"""\
            # Project Charter: {title}

            ## One-sentence purpose

            {description}

            ## Problem

            Describe the exact problem.

            ## Primary users

            {options.audience}

            ## Minimum useful version

            Describe the smallest version that provides real value.

            ## Required capabilities

            - [ ] First approved capability.
            - [ ] Second approved capability.

            ## Non-goals

            - Unapproved first-release features.
            - Architecture added only because it is fashionable.

            ## Platforms

            - [ ] Windows
            - [ ] Ubuntu, Debian, or Kali Linux

            ## Data and privacy

            - Data handled:
            - Sensitive data:
            - Storage location:
            - Retention:
            - Redaction:

            ## Security and authorization

            - Intended environment:
            - Authorization requirements:
            - Allowed users or targets:
            - Prohibited actions:
            - Required evidence:

            ## Success measures

            | Measure | Baseline | Target |
            |---|---:|---:|
            | Define before implementation | Unknown | Approved target |

            ## Definition of done

            Define what must be true before `v0.1.0` is released.
            """
        ),
        "docs/AI_TOOLING.md": dedent(
            """\
            # AI Tooling

            Superpowers controls design, planning, worktrees, TDD, debugging, review, verification,
            and branch completion. Use the smallest relevant Agency roster: Product Manager,
            Software Architect, one implementation specialist, Test Automation Engineer, Code
            Reviewer, AppSec Engineer, DevOps Automator, Technical Writer, and Reality Checker.

            A specialist never overrides the approved specification or security rules. An AI claim
            is not evidence until commands verify it.
            """
        ),
        "docs/START_HERE_WINDOWS.md": dedent(
            """\
            # Start Here on Windows

            1. Open this folder in File Explorer.
            2. Read `README.md`.
            3. Open GitHub Desktop, choose **File > Add local repository**, and select this folder.
            4. Open PowerShell in this folder and run the first-time setup:

            ```powershell
            .\\scripts\\setup.ps1
            ```

            5. Run the project checks:

            ```powershell
            .\\scripts\\check.ps1
            ```

            Setup success ends with `Development setup is ready.` Check success ends with
            `All project checks passed.` If an error appears, read the first failing command,
            do not delete files or disable checks, and remove credentials before sharing logs.
            """
        ),
        "docs/START_HERE_LINUX.md": dedent(
            """\
            # Start Here on Linux

            Supported beginner path: Ubuntu, Debian, and Kali Linux.

            1. Open this folder in Files.
            2. Read `README.md`.
            3. Open a terminal in this folder and run the first-time setup:

            ```bash
            bash scripts/setup.sh
            ```

            4. Run the project checks:

            ```bash
            bash scripts/check.sh
            ```

            Setup success ends with `Development setup is ready.` Check success ends with
            `All project checks passed.` Do not use `sudo` except for documented installation
            steps, and remove credentials before sharing logs.
            """
        ),
        "docs/superpowers/specs/README.md": (
            "# Approved Design Specifications\n\n"
            "Use `YYYY-MM-DD-topic-design.md`. Architectural code requires an approved spec.\n"
        ),
        "docs/superpowers/plans/README.md": (
            "# Approved Implementation Plans\n\n"
            "Use `YYYY-MM-DD-topic-implementation.md`. Include exact files, interfaces, tests, "
            "commands, expected results, documentation changes, and commits.\n"
        ),
        "SECURITY.md": dedent(
            """\
            # Security Policy

            Do not post credentials, private data, or working exploit details in public issues.
            Use private vulnerability reporting or another approved private channel. Include impact,
            affected version, safe reproduction, sanitized logs, and mitigation when known.

            Never commit tokens, passwords, private keys, `.env` files, or customer data. Rotate an
            exposed credential immediately; deleting a visible file does not remove Git history.
            """
        ),
        "CONTRIBUTING.md": dedent(
            """\
            # Contributing

            Work from one small issue on a feature branch. Update approved design materials when
            behavior changes, use red-green-refactor TDD, run the platform check script, inspect the
            diff for secrets and unrelated files, and open a draft PR with evidence and rollback.
            """
        ),
        "CHANGELOG.md": "# Changelog\n\n## [Unreleased]\n\n### Added\n\n- Initial safe project structure.\n",
        "LICENSE": dedent(
            """\
            MIT License

            Copyright (c) 2026 Project Contributors

            Permission is hereby granted, free of charge, to any person obtaining a copy
            of this software and associated documentation files (the "Software"), to deal
            in the Software without restriction, including without limitation the rights
            to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
            copies of the Software, and to permit persons to whom the Software is
            furnished to do so, subject to the following conditions:

            The above copyright notice and this permission notice shall be included in all
            copies or substantial portions of the Software.

            THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
            IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
            FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
            """
        ),
        ".editorconfig": dedent(
            """\
            root = true

            [*]
            charset = utf-8
            end_of_line = lf
            insert_final_newline = true
            indent_style = space
            indent_size = 4
            trim_trailing_whitespace = true

            [*.{md,yml,yaml}]
            indent_size = 2
            trim_trailing_whitespace = false
            """
        ),
        ".gitignore": dedent(
            """\
            .env
            .env.*
            !.env.example
            *.pem
            *.key
            *.pfx
            *.p12
            __pycache__/
            *.py[cod]
            .pytest_cache/
            .mypy_cache/
            .ruff_cache/
            .coverage
            htmlcov/
            .venv/
            dist/
            build/
            *.egg-info/
            .idea/
            .vscode/
            .DS_Store
            Thumbs.db
            logs/
            support-bundles/
            .superpowers/
            """
        ),
        ".github/PULL_REQUEST_TEMPLATE.md": dedent(
            """\
            ## What changed?

            Explain the change in ordinary language.

            ## Why?

            Link the approved requirement, specification, plan, or issue.

            ## Test evidence

            | Command | Result |
            |---|---|
            | `command` | PASS / FAIL |

            ## Security and documentation

            - [ ] No secrets or private data were added.
            - [ ] Input, paths, dependencies, and logs were reviewed.
            - [ ] README, Windows guide, Linux guide, and changelog are accurate.

            ## Risks and rollback

            Risks:

            -

            Rollback:

            -
            """
        ),
        ".github/ISSUE_TEMPLATE/bug_report.yml": dedent(
            """\
            name: Bug report
            description: Report incorrect or unexpected behavior
            title: "[Bug]: "
            labels: ["bug"]
            body:
              - type: markdown
                attributes:
                  value: Never include passwords, tokens, private keys, or private data.
              - type: textarea
                id: summary
                attributes:
                  label: What happened?
                validations:
                  required: true
              - type: textarea
                id: steps
                attributes:
                  label: Safe steps to reproduce
                validations:
                  required: true
              - type: textarea
                id: expected
                attributes:
                  label: Expected result
                validations:
                  required: true
            """
        ),
        ".github/ISSUE_TEMPLATE/feature_request.yml": dedent(
            """\
            name: Feature request
            description: Suggest one user-focused improvement
            title: "[Feature]: "
            labels: ["enhancement"]
            body:
              - type: textarea
                id: problem
                attributes:
                  label: What problem should this solve?
                validations:
                  required: true
              - type: textarea
                id: user
                attributes:
                  label: Who experiences it?
                validations:
                  required: true
              - type: textarea
                id: minimum
                attributes:
                  label: Smallest useful result
                validations:
                  required: true
            """
        ),
        "scripts/setup.ps1": dedent(
            """\
            $ErrorActionPreference = "Stop"
            $Root = Split-Path -Parent $PSScriptRoot
            Set-Location $Root
            if (-not (Test-Path "pyproject.toml")) {
                Write-Host "No application framework is configured yet. Planning files are ready."
                exit 0
            }
            $Launcher = if (Get-Command py -ErrorAction SilentlyContinue) {
                @("py", "-3")
            } else {
                @("python")
            }
            if ($Launcher.Count -eq 2) {
                & $Launcher[0] $Launcher[1] -m venv .venv
            } else {
                & $Launcher[0] -m venv .venv
            }
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
            $Python = Join-Path $Root ".venv\\Scripts\\python.exe"
            & $Python -m pip install --upgrade pip
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
            & $Python -m pip install -e ".[dev]"
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
            Write-Host "Development setup is ready."
            """
        ),
        "scripts/check.ps1": dedent(
            """\
            $ErrorActionPreference = "Stop"
            $Root = Split-Path -Parent $PSScriptRoot
            Set-Location $Root
            Write-Host "Running project checks from $Root"
            if (Test-Path "pyproject.toml") {
                $Python = Join-Path $Root ".venv\\Scripts\\python.exe"
                if (-not (Test-Path $Python)) {
                    throw "Development environment is missing. Run .\\scripts\\setup.ps1 first."
                }
                & $Python -m pytest
                if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                & $Python -m ruff check .
                if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                & $Python -m mypy src tests
                if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
            } else {
                @("README.md", "AGENTS.md", "docs/PROJECT_CHARTER.md") | ForEach-Object {
                    if (-not (Test-Path $_)) { throw "Required file is missing: $_" }
                }
            }
            Write-Host "All project checks passed."
            """
        ),
        "scripts/setup.sh": dedent(
            """\
            #!/usr/bin/env bash
            set -euo pipefail
            root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
            cd "$root"
            if [[ ! -f pyproject.toml ]]; then
              printf 'No application framework is configured yet. Planning files are ready.\\n'
              exit 0
            fi
            python3 -m venv .venv
            .venv/bin/python -m pip install --upgrade pip
            .venv/bin/python -m pip install -e ".[dev]"
            printf 'Development setup is ready.\\n'
            """
        ),
        "scripts/check.sh": dedent(
            """\
            #!/usr/bin/env bash
            set -euo pipefail
            root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
            cd "$root"
            printf 'Running project checks from %s\\n' "$root"
            if [[ -f pyproject.toml ]]; then
              if [[ ! -x .venv/bin/python ]]; then
                printf 'Development environment is missing. Run bash scripts/setup.sh first.\\n' >&2
                exit 1
              fi
              .venv/bin/python -m pytest
              .venv/bin/python -m ruff check .
              .venv/bin/python -m mypy src tests
            else
              for required in README.md AGENTS.md docs/PROJECT_CHARTER.md; do
                if [[ ! -f "$required" ]]; then
                  printf 'Required file is missing: %s\\n' "$required" >&2
                  exit 1
                fi
              done
            fi
            printf 'All project checks passed.\\n'
            """
        ),
    }
    if options.kind is ProjectKind.SECURITY_TOOL:
        files["docs/AUTHORIZATION_AND_SCOPE.md"] = dedent(
            """\
            # Authorization and Scope

            Use only with explicit written authorization.

            - Engagement owner:
            - Authorization location:
            - Target allowlist:
            - Explicit deny list:
            - Permitted window:
            - Emergency contacts:
            - Prohibited actions, including denial of service:
            - Evidence retention:
            - Cleanup requirements:

            An empty allowlist authorizes no targets. Defaults must be non-destructive,
            rate-limited, scope-denying, and fully logged.
            """
        )
    return files


def _python_cli(options: ProjectOptions) -> dict[str, str]:
    module = options.slug.replace("-", "_")
    description = options.description or f"A beginner-created command-line project named {options.name}."
    description_literal = json.dumps(description, ensure_ascii=False)
    return {
        "pyproject.toml": dedent(
            f"""\
            [build-system]
            requires = ["hatchling>=1.27"]
            build-backend = "hatchling.build"

            [project]
            name = "{options.slug}"
            version = "0.1.0"
            description = {description_literal}
            readme = "README.md"
            requires-python = ">=3.11"
            dependencies = []

            [project.optional-dependencies]
            dev = [
              "mypy>=1.17,<2",
              "pytest>=8.4,<10",
              "pytest-cov>=6.2,<8",
              "ruff>=0.12,<1",
            ]

            [project.scripts]
            {options.slug} = "{module}.cli:main"

            [tool.hatch.build.targets.wheel]
            packages = ["src/{module}"]

            [tool.pytest.ini_options]
            addopts = ["--cov={module}", "--cov-branch", "--cov-report=term-missing", "--cov-fail-under=95"]
            testpaths = ["tests"]

            [tool.coverage.run]
            omit = ["src/*/__main__.py"]

            [tool.ruff]
            line-length = 100
            target-version = "py311"

            [tool.ruff.lint]
            select = ["B", "E", "F", "I", "S", "UP"]

            [tool.ruff.lint.per-file-ignores]
            "tests/**/*.py" = ["S101"]

            [tool.mypy]
            python_version = "3.11"
            strict = true
            files = ["src", "tests"]
            """
        ),
        f"src/{module}/__init__.py": '"""Project package."""\n\n__version__ = "0.1.0"\n',
        f"src/{module}/__main__.py": dedent(
            f"""\
            \"\"\"Run with ``python -m {module}``.\"\"\"

            from {module}.cli import main

            if __name__ == "__main__":
                raise SystemExit(main())
            """
        ),
        f"src/{module}/cli.py": dedent(
            f"""\
            \"\"\"Small, testable command-line entry point.\"\"\"

            from __future__ import annotations

            import argparse
            from collections.abc import Sequence


            def parser() -> argparse.ArgumentParser:
                result = argparse.ArgumentParser(description={options.name!r})
                result.add_argument("--name", default="friend", help="Name to greet")
                return result


            def main(argv: Sequence[str] | None = None) -> int:
                args = parser().parse_args(argv)
                print(f"Hello, {{args.name}}!")
                return 0
            """
        ),
        "tests/test_cli.py": dedent(
            f"""\
            import runpy
            import sys

            import pytest

            from {module}.cli import main


            def test_main_greets_requested_name(
                capsys: pytest.CaptureFixture[str],
            ) -> None:
                assert main(["--name", "Grandma"]) == 0
                assert capsys.readouterr().out == "Hello, Grandma!\\n"


            def test_python_module_entrypoint(
                monkeypatch: pytest.MonkeyPatch,
                capsys: pytest.CaptureFixture[str],
            ) -> None:
                runpy.run_module("{module}.__main__", run_name="entrypoint_import_check")
                monkeypatch.setattr(sys, "argv", ["{module}", "--name", "Grandma"])
                with pytest.raises(SystemExit) as exit_info:
                    runpy.run_module("{module}.__main__", run_name="__main__")
                assert exit_info.value.code == 0
                assert capsys.readouterr().out == "Hello, Grandma!\\n"
            """
        ),
    }


def files_for(options: ProjectOptions) -> dict[str, str]:
    files = _common(options)
    if options.kind is ProjectKind.PYTHON_CLI:
        files.update(_python_cli(options))
        files[".github/workflows/ci.yml"] = dedent(
            """\
            name: CI

            on:
              pull_request:
              push:
                branches: [main]

            permissions:
              contents: read

            jobs:
              quality:
                strategy:
                  fail-fast: false
                  matrix:
                    os: [ubuntu-latest, windows-latest]
                    python: ["3.11", "3.12", "3.13"]
                runs-on: ${{ matrix.os }}
                steps:
                  - name: Check out repository
                    uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
                  - name: Set up Python
                    uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065
                    with:
                      python-version: ${{ matrix.python }}
                      cache: pip
                  - name: Install project and checks
                    run: python -m pip install --upgrade pip && python -m pip install -e ".[dev]"
                  - name: Run tests
                    run: python -m pytest
                  - name: Run linting
                    run: python -m ruff check .
                  - name: Run type checking
                    run: python -m mypy src tests
            """
        )
        files[".github/dependabot.yml"] = dedent(
            """\
            version: 2
            updates:
              - package-ecosystem: pip
                directory: /
                schedule:
                  interval: weekly
              - package-ecosystem: github-actions
                directory: /
                schedule:
                  interval: weekly
            """
        )
    else:
        files[".github/workflows/ci.yml"] = dedent(
            """\
            name: Repository structure

            on:
              pull_request:
              push:
                branches: [main]

            permissions:
              contents: read

            jobs:
              structure:
                runs-on: ubuntu-latest
                steps:
                  - name: Check out repository
                    uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
                  - name: Verify required beginner files
                    run: |
                      test -f README.md
                      test -f AGENTS.md
                      test -f SECURITY.md
                      test -f docs/PROJECT_CHARTER.md
                      test -f docs/START_HERE_WINDOWS.md
                      test -f docs/START_HERE_LINUX.md
            """
        )
        files[".github/dependabot.yml"] = dedent(
            """\
            version: 2
            updates:
              - package-ecosystem: github-actions
                directory: /
                schedule:
                  interval: weekly
            """
        )
        files["docs/NEXT_STEPS.md"] = dedent(
            f"""\
            # Next Steps for {options.name}

            The safety and planning structure is ready. The first release generates application
            code only for the Python CLI template. For `{options.kind.value}`, complete the charter,
            use Superpowers brainstorming, approve a written specification and implementation plan,
            and add the smallest working application through test-driven tasks. This avoids silently
            choosing a framework or architecture the owner did not approve.
            """
        )
    return {name: content.rstrip() + "\n" for name, content in files.items()}


def _check_generated_content(files: dict[str, str]) -> None:
    for relative, content in files.items():
        if contains_sensitive(content):
            raise BuilderError(
                "NPB-701",
                f"Possible credential-like value in generated file: {relative}",
            )


class Generator:
    def __init__(self, paths: Paths, log: OperationLog, runner: Runner) -> None:
        self.paths = paths
        self.log = log
        self.runner = runner
        self.backups = Backups(paths.backups)

    def preview(self, options: ProjectOptions) -> tuple[str, ...]:
        files = files_for(options)
        _check_generated_content(files)
        return tuple(sorted(files))

    def generate(
        self,
        options: ProjectOptions,
        *,
        initialize_git: bool = True,
        replace: bool = False,
    ) -> Generation:
        destination = options.destination
        files = files_for(options)
        _check_generated_content(files)
        if destination.exists() and any(destination.iterdir()) and not replace:
            raise BuilderError("NPB-401", str(destination))
        self.log.message(
            "Project generation",
            "\n".join(
                (
                    f"Project: {options.name}",
                    f"Destination: {destination}",
                    f"Kind: {options.kind.value}",
                    f"Visibility: {options.visibility.value}",
                    f"Files: {len(files)}",
                )
            ),
            result="PLANNED" if self.runner.dry_run else "APPROVED",
        )
        if self.runner.dry_run:
            return Generation(
                destination,
                tuple(destination / name for name in sorted(files)),
                (),
                False,
                True,
            )
        destination.mkdir(parents=True, exist_ok=True)
        created: list[Path] = []
        backup_paths: list[Path] = []
        for relative, content in sorted(files.items()):
            target = destination / relative
            existed = target.exists()
            backup = self.backups.write(
                target,
                content,
                project_root=destination,
                replace=replace,
            )
            if not existed:
                created.append(target)
            if backup is not None:
                backup_paths.append(backup)
        git_initialized = self._git_init(destination) if initialize_git else False
        self.log.message(
            "Project generation",
            f"Created {len(created)} files; backups {len(backup_paths)}; Git {git_initialized}.",
            result="PASS",
        )
        return Generation(
            destination,
            tuple(created),
            tuple(backup_paths),
            git_initialized,
            False,
        )

    def _git_init(self, destination: Path) -> bool:
        if not shutil.which("git"):
            self.log.message(
                "Initialize Git",
                "Git is not installed. Files were created safely without Git.",
                result="SKIPPED",
            )
            return False
        if (destination / ".git").exists():
            self.log.message("Initialize Git", "Existing repository detected.", result="SKIPPED")
            return True
        result = self.runner.run(
            ("git", "init", "-b", "main"),
            step="Initialize Git repository",
            cwd=destination,
            error_code="NPB-501",
        )
        if not result.ok:
            raise BuilderError("NPB-501", result.stderr or result.stdout)
        return True
