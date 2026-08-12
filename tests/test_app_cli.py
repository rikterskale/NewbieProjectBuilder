from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from newbie_project_builder import cli
from newbie_project_builder.app import Application
from newbie_project_builder.console import Console
from newbie_project_builder.errors import BuilderError
from newbie_project_builder.integrations import Integration
from newbie_project_builder.models import (
    Check,
    CommandResult,
    Host,
    LinuxKind,
    OSKind,
    ProjectKind,
    ProjectOptions,
    Tool,
    Visibility,
)


class SequenceConsole(Console):
    def __init__(self, answers: list[str]) -> None:
        self.answers = iter(answers)
        self.output: list[str] = []
        super().__init__(input_func=lambda prompt: next(self.answers), output_func=self.output.append)


class FakeRunner:
    def __init__(self, responses: list[tuple[int, str, str]]) -> None:
        self.responses = list(responses)
        self.commands: list[tuple[str, ...]] = []
        self.dry_run = False

    def run(self, command: tuple[str, ...], **kwargs: object) -> CommandResult:
        self.commands.append(tuple(command))
        code, stdout, stderr = self.responses.pop(0)
        return CommandResult(tuple(command), code, stdout, stderr, 0, datetime.now(UTC))


class FakePreflight:
    def __init__(self, checks: tuple[Check, ...], tools: tuple[Tool, ...] = ()) -> None:
        self.checks = checks
        self.tool_values = tools

    def run(self, path: Path) -> tuple[Check, ...]:
        return self.checks

    def tools(self) -> tuple[Tool, ...]:
        return self.tool_values


class FakeInstaller:
    def __init__(self, success: bool = True) -> None:
        self.success = success
        self.plans: list[str] = []
        self.executed: list[Any] = []

    def plan(self, key: str) -> Any:
        from newbie_project_builder.installer import InstallPlan

        self.plans.append(key)
        if key == "bad":
            raise BuilderError("NPB-010")
        return InstallPlan(key, key.upper(), "explanation", (("install", key),))

    def execute(self, plan: Any) -> bool:
        self.executed.append(plan)
        return self.success


class FakeIntegrations:
    def __init__(self, success: bool = True) -> None:
        self.success = success
        self.install_calls = 0

    def statuses(self) -> tuple[Integration, ...]:
        return (
            Integration("One", True, "available", "none"),
            Integration("Two", False, "missing", "install"),
        )

    def install_core_agents(self) -> bool:
        self.install_calls += 1
        return self.success


class FakeGitHub:
    def __init__(self, *, signed_in: bool = True, login: bool = True) -> None:
        self._signed_in = signed_in
        self._login = login
        self.created = 0
        self.published = 0

    def signed_in(self) -> bool:
        return self._signed_in

    def browser_login(self) -> bool:
        self._signed_in = self._login
        return self._login

    def account(self) -> Any:
        from newbie_project_builder.github import Account

        return Account("rikter")

    def create_repository(self, *args: object, **kwargs: object) -> bool:
        self.created += 1
        return True

    def publish_initial_main(self, project: Path) -> bool:
        self.published += 1
        return True


def linux_host() -> Host:
    return Host(OSKind.LINUX, LinuxKind.APT, "Linux", "6", "x", "debian", "Debian", "13")


def test_banner_and_diagnostics_pass_fail(tmp_path: Path) -> None:
    console = SequenceConsole([])
    app = Application(home=tmp_path / "home", console=console, host=linux_host())
    app.banner()
    assert any("NEWBIE PROJECT BUILDER" in line for line in console.output)
    app.preflight = FakePreflight((Check("OK", "Thing", True, "good"),))  # type: ignore[assignment]
    assert app.diagnostics() == 0
    app.preflight = FakePreflight((Check("BAD", "Thing", False, "bad", "fix"),))  # type: ignore[assignment]
    assert app.diagnostics() == 2
    assert any("Fix: fix" in line for line in console.output)


def test_setup_installs_selected_tools_and_handles_failure(tmp_path: Path) -> None:
    console = SequenceConsole(["yes", "no"])
    app = Application(home=tmp_path / "home", console=console, host=linux_host())
    tools = (
        Tool("git", "Git", "git", False),
        Tool("gh", "GH", "gh", False, required=False),
    )
    app.preflight = FakePreflight((Check("OK", "OS", True, "good"),), tools)  # type: ignore[assignment]
    installer = FakeInstaller()
    app.installer = installer  # type: ignore[assignment]
    app.integrations = FakeIntegrations()  # type: ignore[assignment]
    assert app.setup() == 0
    assert installer.plans == ["git", "gh"]
    assert len(installer.executed) == 1
    assert app.state.load() is not None

    failing_console = SequenceConsole(["yes"])
    failing = Application(home=tmp_path / "failed", console=failing_console, host=linux_host())
    failing.preflight = FakePreflight((Check("OK", "OS", True, "good"),), (tools[0],))  # type: ignore[assignment]
    failing.installer = FakeInstaller(success=False)  # type: ignore[assignment]
    assert failing.setup() == 1
    assert failing.state.load().last_error == "NPB-901"  # type: ignore[union-attr]


def test_show_and_install_integrations(tmp_path: Path) -> None:
    console = SequenceConsole(["no"])
    app = Application(home=tmp_path / "home", console=console, host=linux_host())
    fake = FakeIntegrations()
    app.integrations = fake  # type: ignore[assignment]
    assert app.show_integrations() == 0
    assert app.install_agency() == 0
    assert fake.install_calls == 0
    app.console = SequenceConsole(["yes"])
    assert app.install_agency() == 0
    assert fake.install_calls == 1
    app.integrations = FakeIntegrations(success=False)  # type: ignore[assignment]
    app.console = SequenceConsole(["yes"])
    assert app.install_agency() == 1


def test_project_wizard_dry_run(tmp_path: Path) -> None:
    console = SequenceConsole(
        [
            "Demo Tool",
            "2",
            "My family",
            "3",
            str(tmp_path),
            "Helps my family.",
            "CREATE PROJECT",
        ]
    )
    app = Application(home=tmp_path / "home", dry_run=True, console=console, host=linux_host())
    assert app.project_wizard() == 0
    assert not (tmp_path / "demo-tool").exists()
    assert any("Preview mode" in line for line in console.output)


def test_project_wizard_cancel_and_noninteractive(tmp_path: Path) -> None:
    console = SequenceConsole(
        ["Demo", "1", "Me", "3", str(tmp_path), "Purpose", "cancel"]
    )
    app = Application(home=tmp_path / "home", console=console, host=linux_host())
    assert app.project_wizard() == 0
    assert not (tmp_path / "demo").exists()
    options = ProjectOptions(
        "Demo", "demo", ProjectKind.GENERIC, "Me", Visibility.LOCAL_ONLY, tmp_path
    )
    assert app.create_noninteractive(options, initialize_git=False) == 0
    assert (tmp_path / "demo" / "README.md").exists()


def test_initial_commit_sets_project_only_identity(tmp_path: Path) -> None:
    console = SequenceConsole(["Rikter", "rikter@example.test"])
    app = Application(home=tmp_path / "home", console=console, host=linux_host())
    runner = FakeRunner(
        [
            (1, "", ""),
            (1, "", ""),
            (0, "", ""),
            (0, "", ""),
            (0, "", ""),
            (0, "", ""),
        ]
    )
    app.runner = runner  # type: ignore[assignment]
    app._initial_commit(tmp_path)
    assert ("git", "config", "user.name", "Rikter") in runner.commands
    assert ("git", "config", "user.email", "rikter@example.test") in runner.commands
    assert runner.commands[-1][:3] == ("git", "commit", "-m")


def test_initial_commit_existing_identity_and_failures(tmp_path: Path) -> None:
    app = Application(home=tmp_path / "home", console=SequenceConsole([]), host=linux_host())
    runner = FakeRunner([(0, "Name", ""), (0, "mail", ""), (0, "", ""), (0, "", "")])
    app.runner = runner  # type: ignore[assignment]
    app._initial_commit(tmp_path)
    assert len(runner.commands) == 4

    add_fail = Application(home=tmp_path / "add", console=SequenceConsole([]), host=linux_host())
    add_fail.runner = FakeRunner([(0, "Name", ""), (0, "mail", ""), (1, "", "bad")])  # type: ignore[assignment]
    with pytest.raises(BuilderError):
        add_fail._initial_commit(tmp_path)
    commit_fail = Application(home=tmp_path / "commit", console=SequenceConsole([]), host=linux_host())
    commit_fail.runner = FakeRunner(
        [(0, "Name", ""), (0, "mail", ""), (0, "", ""), (1, "", "bad")]
    )  # type: ignore[assignment]
    with pytest.raises(BuilderError):
        commit_fail._initial_commit(tmp_path)


def test_offer_github_missing_declined_login_public_and_publish(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    options = ProjectOptions(
        "Demo", "demo", ProjectKind.GENERIC, "Me", Visibility.PRIVATE, tmp_path
    )
    console = SequenceConsole([])
    app = Application(home=tmp_path / "home", console=console, host=linux_host())
    monkeypatch.setattr("newbie_project_builder.app.shutil.which", lambda name: None)
    app._offer_github(options, tmp_path)
    assert any("missing" in line.lower() for line in console.output)

    monkeypatch.setattr("newbie_project_builder.app.shutil.which", lambda name: "/gh")
    app.console = SequenceConsole(["no"])
    app.github = FakeGitHub(signed_in=False)  # type: ignore[assignment]
    app._offer_github(options, tmp_path)
    assert app.github.created == 0  # type: ignore[attr-defined]

    app.console = SequenceConsole(["yes"])
    app.github = FakeGitHub(signed_in=False, login=False)  # type: ignore[assignment]
    with pytest.raises(BuilderError):
        app._offer_github(options, tmp_path)

    public = ProjectOptions(
        "Demo", "demo", ProjectKind.GENERIC, "Me", Visibility.PUBLIC, tmp_path
    )
    app.console = SequenceConsole(["WRONG"])
    app.github = FakeGitHub()  # type: ignore[assignment]
    app._offer_github(public, tmp_path)
    assert app.github.created == 0  # type: ignore[attr-defined]

    app.console = SequenceConsole(["MAKE PUBLIC", "yes", "yes"])
    app.github = FakeGitHub()  # type: ignore[assignment]
    app._offer_github(public, tmp_path)
    assert app.github.created == 1  # type: ignore[attr-defined]
    assert app.github.published == 1  # type: ignore[attr-defined]


def test_support_latest_and_cleanup(tmp_path: Path) -> None:
    console = SequenceConsole([])
    app = Application(home=tmp_path / "home", console=console, host=linux_host())
    assert app.latest_log() == 0
    assert app.support_bundle() == 0
    assert any("Sanitized support bundle" in line for line in console.output)

    cancel = Application(home=tmp_path / "cancel", console=SequenceConsole(["NO"]), host=linux_host())
    assert cancel.cleanup() == 0
    assert cancel.paths.logs.exists()
    clean = Application(home=tmp_path / "clean", console=SequenceConsole(["DELETE BUILDER DATA"]), host=linux_host())
    clean.paths.state.write_text("{}", encoding="utf-8")
    assert clean.cleanup() == 0
    assert clean.paths.logs.exists()
    assert not clean.log.path.exists()
    assert not clean.paths.state.exists()


def test_menu_immediate_exit_and_error_recovery(tmp_path: Path) -> None:
    exit_console = SequenceConsole(["9"])
    assert Application(home=tmp_path / "exit", console=exit_console, host=linux_host()).menu() == 0
    assert any("Goodbye" in line for line in exit_console.output)

    console = SequenceConsole(["3", "9"])
    app = Application(home=tmp_path / "menu", console=console, host=linux_host())
    app.preflight = FakePreflight((Check("BAD", "Broken", False, "bad", "fix"),))  # type: ignore[assignment]
    assert app.menu() == 0


def test_cli_parser_version_create_and_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    parsed = cli.parser().parse_args(["diagnose"])
    assert parsed.command == "diagnose"
    assert cli.main(["version"]) == 0
    assert "0.1.0" in capsys.readouterr().out
    assert (
        cli.main(
            [
                "--home",
                str(tmp_path / "home"),
                "create",
                "--name",
                "Demo",
                "--parent",
                str(tmp_path),
                "--no-git",
            ]
        )
        == 0
    )
    assert (tmp_path / "demo" / "README.md").exists()

    class BrokenApp:
        def __init__(self, **kwargs: object) -> None:
            class Log:
                path = Path("log.txt")

                def message(self, *args: object, **kwargs: object) -> None:
                    pass

            self.log = Log()

        def diagnostics(self) -> int:
            raise BuilderError("NPB-101")

        def banner(self) -> None:
            pass

    monkeypatch.setattr(cli, "Application", BrokenApp)
    assert cli.main(["diagnose"]) == 1
    assert "NPB-101" in capsys.readouterr().err


def test_cli_routes_and_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    calls: list[str] = []

    class RoutedApp:
        def __init__(self, **kwargs: object) -> None:
            class Log:
                path = Path("log")

                def message(self, *args: object, **kwargs: object) -> None:
                    pass

            self.log = Log()

        def banner(self) -> None:
            calls.append("banner")

        def menu(self) -> int:
            calls.append("menu")
            return 0

        def setup(self) -> int:
            calls.append("setup")
            return 0

        def show_integrations(self) -> int:
            calls.append("integrations")
            return 0

        def support_bundle(self) -> int:
            calls.append("support")
            return 0

        def latest_log(self) -> int:
            calls.append("latest")
            return 0

        def diagnostics(self) -> int:
            calls.append("diagnose")
            return 0

    monkeypatch.setattr(cli, "Application", RoutedApp)
    assert cli.main([]) == 0
    assert cli.main(["setup"]) == 0
    assert cli.main(["integrations"]) == 0
    assert cli.main(["support-bundle"]) == 0
    assert cli.main(["latest-log"]) == 0
    assert "menu" in calls and "support" in calls

    class InterruptApp(RoutedApp):
        def menu(self) -> int:
            raise KeyboardInterrupt

    monkeypatch.setattr(cli, "Application", InterruptApp)
    assert cli.main([]) == 130
    assert "Cancelled" in capsys.readouterr().err
