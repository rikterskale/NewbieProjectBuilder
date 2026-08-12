"""Typed models shared by the builder."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path


class OSKind(StrEnum):
    WINDOWS = "windows"
    LINUX = "linux"
    OTHER = "other"


class LinuxKind(StrEnum):
    APT = "apt"
    OTHER = "other"
    NONE = "none"


class ProjectKind(StrEnum):
    GENERIC = "generic"
    PYTHON_CLI = "python-cli"
    WEB_APP = "web-app"
    WEB_API = "web-api"
    DESKTOP_APP = "desktop-app"
    AI_APP = "ai-app"
    SECURITY_TOOL = "authorized-security-tool"


class Visibility(StrEnum):
    PRIVATE = "private"
    PUBLIC = "public"
    LOCAL_ONLY = "local-only"


@dataclass(frozen=True, slots=True)
class Paths:
    home: Path
    logs: Path
    state: Path
    backups: Path
    support: Path
    integrations: Path

    @classmethod
    def create(cls, home: Path) -> Paths:
        resolved = home.expanduser().resolve()
        return cls(
            home=resolved,
            logs=resolved / "logs",
            state=resolved / ".builder-state.json",
            backups=resolved / "backups",
            support=resolved / "support",
            integrations=resolved / "integrations",
        )

    @property
    def marker(self) -> Path:
        return self.home / ".newbie-project-builder-managed"

    def ensure(self) -> None:
        for directory in (self.home, self.logs, self.backups, self.support, self.integrations):
            directory.mkdir(parents=True, exist_ok=True)
        self.marker.write_text(
            "This folder is managed by Newbie Project Builder.\n",
            encoding="utf-8",
        )


@dataclass(frozen=True, slots=True)
class Host:
    os_kind: OSKind
    linux_kind: LinuxKind
    system: str
    release: str
    machine: str
    distro_id: str = ""
    distro_name: str = ""
    distro_version: str = ""

    @property
    def supported(self) -> bool:
        return self.os_kind is OSKind.WINDOWS or (
            self.os_kind is OSKind.LINUX and self.linux_kind is LinuxKind.APT
        )

    @property
    def display_name(self) -> str:
        if self.os_kind is OSKind.WINDOWS:
            return f"Windows {self.release}".strip()
        if self.os_kind is OSKind.LINUX:
            return f"{self.distro_name or self.distro_id or 'Linux'} {self.distro_version}".strip()
        return f"{self.system} {self.release}".strip()


@dataclass(frozen=True, slots=True)
class Check:
    code: str
    label: str
    passed: bool
    details: str
    fix: str = ""
    required: bool = True

    @property
    def marker(self) -> str:
        if self.passed:
            return "PASS"
        return "FIX " if self.required else "WARN"


@dataclass(frozen=True, slots=True)
class Tool:
    key: str
    name: str
    command: str
    installed: bool
    path: str = ""
    version: str = ""
    required: bool = True


@dataclass(frozen=True, slots=True)
class CommandResult:
    command: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    started_at: datetime
    dry_run: bool = False

    @property
    def ok(self) -> bool:
        return self.exit_code == 0


@dataclass(frozen=True, slots=True)
class ProjectOptions:
    name: str
    slug: str
    kind: ProjectKind
    audience: str
    visibility: Visibility
    parent: Path
    description: str = ""

    @property
    def destination(self) -> Path:
        return self.parent.expanduser().resolve() / self.slug


@dataclass(slots=True)
class WorkflowState:
    operation_id: str
    workflow: str
    completed_steps: list[str] = field(default_factory=list)
    next_step: str = ""
    last_error: str | None = None
    updated_at: str = ""
