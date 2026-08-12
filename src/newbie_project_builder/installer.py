"""Exact package-manager plans that require explicit UI confirmation."""

from __future__ import annotations

from dataclasses import dataclass

from newbie_project_builder.commands import Runner
from newbie_project_builder.errors import BuilderError
from newbie_project_builder.models import Host, LinuxKind, OSKind


@dataclass(frozen=True, slots=True)
class InstallPlan:
    key: str
    name: str
    explanation: str
    commands: tuple[tuple[str, ...], ...]
    may_request_admin: bool = True


_WINDOWS = {
    "git": ("Git", "Git.Git"),
    "gh": ("GitHub CLI", "GitHub.cli"),
    "python": ("Python 3.12", "Python.Python.3.12"),
    "github_desktop": ("GitHub Desktop", "GitHub.GitHubDesktop"),
}
_APT = {
    "git": ("Git", "git"),
    "gh": ("GitHub CLI", "gh"),
    "python": ("Python 3", "python3", "python3-venv", "python3-pip"),
}


class Installer:
    def __init__(self, host: Host, runner: Runner) -> None:
        self.host = host
        self.runner = runner

    def plan(self, key: str) -> InstallPlan:
        if self.host.os_kind is OSKind.WINDOWS:
            if key == "codex":
                raise BuilderError("NPB-104")
            if key not in _WINDOWS:
                raise BuilderError("NPB-010", f"No approved WinGet package for {key}.")
            name, package_id = _WINDOWS[key]
            return InstallPlan(
                key,
                name,
                f"Install {name} using exact WinGet package ID {package_id}.",
                (
                    (
                        "winget",
                        "install",
                        "--id",
                        package_id,
                        "--exact",
                        "--accept-source-agreements",
                        "--accept-package-agreements",
                    ),
                ),
            )
        if self.host.os_kind is OSKind.LINUX and self.host.linux_kind is LinuxKind.APT:
            if key == "codex":
                raise BuilderError("NPB-104")
            if key not in _APT:
                raise BuilderError("NPB-011", f"No approved APT package for {key}.")
            name, *packages = _APT[key]
            return InstallPlan(
                key,
                name,
                (
                    f"Refresh APT metadata, then install {name}. Linux may ask for your "
                    "password directly through sudo; the builder does not store it."
                ),
                (
                    ("sudo", "apt-get", "update"),
                    ("sudo", "apt-get", "install", "-y", *packages),
                ),
            )
        raise BuilderError("NPB-001", self.host.display_name)

    def execute(self, plan: InstallPlan) -> bool:
        for index, command in enumerate(plan.commands, 1):
            result = self.runner.run(
                command,
                step=f"Install {plan.name} ({index}/{len(plan.commands)})",
                timeout=900,
                error_code="NPB-010" if self.host.os_kind is OSKind.WINDOWS else "NPB-011",
            )
            if not result.ok:
                return False
        return True
