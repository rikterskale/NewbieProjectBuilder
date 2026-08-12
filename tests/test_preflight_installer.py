from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from newbie_project_builder.errors import BuilderError
from newbie_project_builder.installer import Installer, InstallPlan
from newbie_project_builder.models import CommandResult, Host, LinuxKind, OSKind
from newbie_project_builder.preflight import Preflight


@dataclass
class Usage:
    free: int


class Connection:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class FakeRunner:
    def __init__(self, exit_codes: list[int] | None = None) -> None:
        self.exit_codes = list(exit_codes or [0])
        self.commands: list[tuple[str, ...]] = []

    def run(self, command: tuple[str, ...], **kwargs: object) -> CommandResult:
        from datetime import UTC, datetime

        self.commands.append(tuple(command))
        code = self.exit_codes.pop(0) if self.exit_codes else 0
        return CommandResult(tuple(command), code, "", "bad" if code else "", 0, datetime.now(UTC))


def test_preflight_supported_and_failing_checks(tmp_path: Path) -> None:
    connection = Connection()
    host = Host(OSKind.LINUX, LinuxKind.APT, "Linux", "6", "x86", "kali", "Kali", "2026")
    preflight = Preflight(
        host=host,
        which=lambda command: f"/usr/bin/{command}" if command != "codex" else None,
        disk_usage=lambda path: Usage(3 * 1024**3),
        connect=lambda *args, **kwargs: connection,
    )
    checks = preflight.run(tmp_path)
    assert checks[0].passed
    assert checks[1].passed
    assert checks[2].passed
    assert connection.closed
    codex = next(check for check in checks if check.label == "Codex CLI")
    assert not codex.passed and not codex.required and codex.marker == "WARN"
    apt = next(tool for tool in preflight.tools() if tool.key == "apt")
    assert apt.installed


def test_preflight_unsupported_low_disk_and_no_network(tmp_path: Path) -> None:
    host = Host(OSKind.OTHER, LinuxKind.NONE, "Plan9", "1", "x")

    def no_network(*args: object, **kwargs: object) -> Connection:
        raise OSError("offline")

    preflight = Preflight(
        host=host,
        which=lambda command: None,
        disk_usage=lambda path: Usage(100),
        connect=no_network,
    )
    assert preflight.operating_system().code == "NPB-001"
    assert preflight.disk(tmp_path).code == "NPB-002"
    internet = preflight.internet()
    assert internet.code == "NPB-003" and not internet.required
    assert all(not tool.installed for tool in preflight.tools() if tool.key != "python")


def test_windows_tool_detection(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    desktop = tmp_path / "AppData" / "Local" / "GitHubDesktop" / "GitHubDesktop.exe"
    desktop.parent.mkdir(parents=True)
    desktop.write_text("x", encoding="utf-8")
    host = Host(OSKind.WINDOWS, LinuxKind.NONE, "Windows", "11", "AMD64")
    tools = Preflight(host=host, which=lambda command: None).tools()
    assert next(tool for tool in tools if tool.key == "github_desktop").installed
    assert any(tool.key == "winget" for tool in tools)


def test_windows_install_plans_and_execute() -> None:
    host = Host(OSKind.WINDOWS, LinuxKind.NONE, "Windows", "11", "AMD64")
    runner = FakeRunner()
    installer = Installer(host, runner)  # type: ignore[arg-type]
    plan = installer.plan("git")
    assert plan.name == "Git"
    assert plan.commands[0][0] == "winget"
    assert "Git.Git" in plan.commands[0]
    assert installer.execute(plan)
    assert runner.commands == [plan.commands[0]]
    with pytest.raises(BuilderError) as codex:
        installer.plan("codex")
    assert codex.value.code == "NPB-104"
    with pytest.raises(BuilderError) as unknown:
        installer.plan("unknown")
    assert unknown.value.code == "NPB-010"


def test_apt_plan_execute_stops_on_failure() -> None:
    host = Host(OSKind.LINUX, LinuxKind.APT, "Linux", "6", "x", "debian", "Debian", "13")
    runner = FakeRunner([0, 1])
    installer = Installer(host, runner)  # type: ignore[arg-type]
    plan = installer.plan("python")
    assert plan.commands[0] == ("sudo", "apt-get", "update")
    assert "python3-venv" in plan.commands[1]
    assert not installer.execute(plan)
    assert len(runner.commands) == 2
    with pytest.raises(BuilderError) as unknown:
        installer.plan("desktop")
    assert unknown.value.code == "NPB-011"


def test_unsupported_installer() -> None:
    host = Host(OSKind.LINUX, LinuxKind.OTHER, "Linux", "6", "x", "fedora", "Fedora", "43")
    installer = Installer(host, FakeRunner())  # type: ignore[arg-type]
    with pytest.raises(BuilderError) as caught:
        installer.plan("git")
    assert caught.value.code == "NPB-001"


def test_install_plan_defaults() -> None:
    plan = InstallPlan("x", "X", "explain", (("x",),))
    assert plan.may_request_admin
