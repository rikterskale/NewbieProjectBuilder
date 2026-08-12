"""Explicit GitHub CLI operations; no token collection or implicit publish."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from newbie_project_builder.commands import Runner
from newbie_project_builder.errors import BuilderError
from newbie_project_builder.models import Visibility


@dataclass(frozen=True, slots=True)
class Account:
    login: str
    host: str = "github.com"


class GitHub:
    def __init__(self, runner: Runner) -> None:
        self.runner = runner

    def signed_in(self) -> bool:
        return self.runner.run(
            ("gh", "auth", "status"),
            step="Check GitHub sign-in",
            error_code="NPB-201",
            log_output=False,
        ).ok

    def browser_login(self) -> bool:
        return self.runner.run(
            ("gh", "auth", "login", "--web", "--git-protocol", "https"),
            step="Sign in to GitHub in browser",
            timeout=900,
            error_code="NPB-201",
            log_output=False,
        ).ok

    def account(self) -> Account:
        result = self.runner.run(
            ("gh", "api", "user"),
            step="Read active GitHub account",
            error_code="NPB-201",
            log_output=False,
        )
        if not result.ok:
            raise BuilderError("NPB-201", result.stderr or result.stdout)
        try:
            login = str(json.loads(result.stdout)["login"])
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise BuilderError("NPB-201", "GitHub account response was not understood.") from exc
        return Account(login)

    def create_repository(
        self,
        project: Path,
        *,
        name: str,
        visibility: Visibility,
        description: str = "",
    ) -> bool:
        if visibility is Visibility.LOCAL_ONLY:
            return False
        flag = "--private" if visibility is Visibility.PRIVATE else "--public"
        command = [
            "gh",
            "repo",
            "create",
            name,
            flag,
            "--source",
            str(project),
            "--remote",
            "origin",
        ]
        if description:
            command.extend(("--description", description))
        display = list(command)
        if "--description" in display:
            index = display.index("--description") + 1
            display[index] = "<DESCRIPTION>"
        result = self.runner.run(
            command,
            step="Create GitHub repository",
            cwd=project,
            timeout=300,
            error_code="NPB-403",
            display_command=display,
        )
        if not result.ok:
            raise BuilderError("NPB-403", result.stderr or result.stdout)
        return True

    def publish_initial_main(self, project: Path) -> bool:
        result = self.runner.run(
            ("git", "push", "-u", "origin", "main"),
            step="Publish initial main branch",
            cwd=project,
            timeout=600,
            error_code="NPB-503",
        )
        if not result.ok:
            raise BuilderError("NPB-503", result.stderr or result.stdout)
        return True

    def push_feature(self, project: Path) -> bool:
        branch = self.runner.run(
            ("git", "branch", "--show-current"),
            step="Read current branch",
            cwd=project,
            error_code="NPB-501",
        )
        name = branch.stdout.strip()
        if not branch.ok or not name:
            raise BuilderError("NPB-501", branch.stderr or "No branch was found.")
        if name in {"main", "master"}:
            raise BuilderError("NPB-502", f"Current branch: {name}")
        result = self.runner.run(
            ("git", "push", "-u", "origin", name),
            step="Push feature branch",
            cwd=project,
            timeout=600,
            error_code="NPB-503",
        )
        if not result.ok:
            raise BuilderError("NPB-503", result.stderr or result.stdout)
        return True

    def draft_pr(self, project: Path, *, title: str, body_file: Path, base: str = "main") -> bool:
        result = self.runner.run(
            (
                "gh",
                "pr",
                "create",
                "--draft",
                "--title",
                title,
                "--body-file",
                str(body_file),
                "--base",
                base,
            ),
            step="Create draft pull request",
            cwd=project,
            timeout=300,
            error_code="NPB-203",
        )
        if not result.ok:
            raise BuilderError("NPB-203", result.stderr or result.stdout)
        return True
