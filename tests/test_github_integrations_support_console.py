from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from newbie_project_builder.console import Console
from newbie_project_builder.errors import BuilderError
from newbie_project_builder.github import GitHub
from newbie_project_builder.integrations import CORE_AGENTS, Integrations
from newbie_project_builder.models import CommandResult, Host, LinuxKind, OSKind, Paths, Visibility
from newbie_project_builder.support import Support, members


class FakeLog:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str, str]] = []

    def message(self, step: str, message: str, *, result: str = "INFO") -> None:
        self.messages.append((step, message, result))


class QueueRunner:
    def __init__(self, results: list[tuple[int, str, str]] | None = None) -> None:
        self.results = list(results or [(0, "", "")])
        self.commands: list[tuple[str, ...]] = []
        self.log = FakeLog()

    def run(self, command: tuple[str, ...] | list[str], **kwargs: object) -> CommandResult:
        self.commands.append(tuple(command))
        code, stdout, stderr = self.results.pop(0) if self.results else (0, "", "")
        return CommandResult(
            tuple(command), code, stdout, stderr, 0, datetime.now(UTC), False
        )


def test_github_auth_login_account_and_create(tmp_path: Path) -> None:
    runner = QueueRunner([(0, "", ""), (0, "", ""), (0, '{"login":"rikter"}', ""), (0, "", "")])
    service = GitHub(runner)  # type: ignore[arg-type]
    assert service.signed_in()
    assert service.browser_login()
    assert service.account().login == "rikter"
    assert service.create_repository(
        tmp_path,
        name="demo",
        visibility=Visibility.PRIVATE,
        description="Demo project",
    )
    command = runner.commands[-1]
    assert "--private" in command and "--description" in command
    assert not service.create_repository(
        tmp_path, name="local", visibility=Visibility.LOCAL_ONLY
    )


def test_github_failures_and_public_creation(tmp_path: Path) -> None:
    assert not GitHub(QueueRunner([(1, "", "no auth")])).signed_in()  # type: ignore[arg-type]
    assert not GitHub(QueueRunner([(1, "", "cancelled")])).browser_login()  # type: ignore[arg-type]
    with pytest.raises(BuilderError) as auth:
        GitHub(QueueRunner([(1, "", "bad")])).account()  # type: ignore[arg-type]
    assert auth.value.code == "NPB-201"
    with pytest.raises(BuilderError):
        GitHub(QueueRunner([(0, "not-json", "")])).account()  # type: ignore[arg-type]
    public_runner = QueueRunner([(0, "", "")])
    assert GitHub(public_runner).create_repository(  # type: ignore[arg-type]
        tmp_path, name="demo", visibility=Visibility.PUBLIC
    )
    assert "--public" in public_runner.commands[0]
    with pytest.raises(BuilderError) as create:
        GitHub(QueueRunner([(1, "", "exists")])).create_repository(  # type: ignore[arg-type]
            tmp_path, name="demo", visibility=Visibility.PRIVATE
        )
    assert create.value.code == "NPB-403"


def test_github_push_and_pr_paths(tmp_path: Path) -> None:
    service = GitHub(QueueRunner([(0, "", "")]))  # type: ignore[arg-type]
    assert service.publish_initial_main(tmp_path)
    with pytest.raises(BuilderError) as initial:
        GitHub(QueueRunner([(1, "", "denied")])).publish_initial_main(tmp_path)  # type: ignore[arg-type]
    assert initial.value.code == "NPB-503"

    feature = QueueRunner([(0, "agent/demo\n", ""), (0, "", "")])
    assert GitHub(feature).push_feature(tmp_path)  # type: ignore[arg-type]
    assert feature.commands[-1] == ("git", "push", "-u", "origin", "agent/demo")
    with pytest.raises(BuilderError) as main:
        GitHub(QueueRunner([(0, "main\n", "")])).push_feature(tmp_path)  # type: ignore[arg-type]
    assert main.value.code == "NPB-502"
    with pytest.raises(BuilderError) as no_branch:
        GitHub(QueueRunner([(1, "", "bad")])).push_feature(tmp_path)  # type: ignore[arg-type]
    assert no_branch.value.code == "NPB-501"
    with pytest.raises(BuilderError) as rejected:
        GitHub(QueueRunner([(0, "agent/x\n", ""), (1, "", "rejected")])).push_feature(  # type: ignore[arg-type]
            tmp_path
        )
    assert rejected.value.code == "NPB-503"

    body = tmp_path / "body.md"
    body.write_text("body", encoding="utf-8")
    assert GitHub(QueueRunner([(0, "", "")])).draft_pr(  # type: ignore[arg-type]
        tmp_path, title="Demo", body_file=body
    )
    with pytest.raises(BuilderError) as pr:
        GitHub(QueueRunner([(1, "", "forbidden")])).draft_pr(  # type: ignore[arg-type]
            tmp_path, title="Demo", body_file=body
        )
    assert pr.value.code == "NPB-203"


def test_integration_statuses(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setattr("newbie_project_builder.integrations.shutil.which", lambda name: f"/{name}")
    plugin = tmp_path / ".codex" / "plugins" / "superpowers"
    plugin.mkdir(parents=True)
    agents = tmp_path / ".codex" / "agents"
    agents.mkdir(parents=True)
    for name in CORE_AGENTS:
        (agents / f"{name}.toml").write_text("x", encoding="utf-8")
    statuses = Integrations(Paths.create(tmp_path / "builder"), QueueRunner()).statuses()  # type: ignore[arg-type]
    assert all(status.available for status in statuses)

    monkeypatch.setattr("newbie_project_builder.integrations.shutil.which", lambda name: None)
    for path in agents.glob("*.toml"):
        path.unlink()
    plugin.rmdir()
    statuses = Integrations(Paths.create(tmp_path / "builder2"), QueueRunner()).statuses()  # type: ignore[arg-type]
    assert not any(status.available for status in statuses)


def test_agency_clone_existing_new_and_fail(tmp_path: Path) -> None:
    paths = Paths.create(tmp_path / "builder")
    checkout = paths.integrations / "agency-agents"
    (checkout / ".git").mkdir(parents=True)
    runner = QueueRunner()
    manager = Integrations(paths, runner)  # type: ignore[arg-type]
    assert manager.clone_agency() == checkout
    assert not runner.commands
    assert runner.log.messages[-1][2] == "SKIPPED"

    other_paths = Paths.create(tmp_path / "other")
    bad = other_paths.integrations / "agency-agents"
    bad.mkdir(parents=True)
    with pytest.raises(BuilderError):
        Integrations(other_paths, QueueRunner()).clone_agency()  # type: ignore[arg-type]

    fresh_paths = Paths.create(tmp_path / "fresh")
    success = QueueRunner([(0, "", "")])
    assert Integrations(fresh_paths, success).clone_agency() == fresh_paths.integrations / "agency-agents"  # type: ignore[arg-type]
    assert success.commands[0][:3] == ("git", "clone", "--depth")
    with pytest.raises(BuilderError) as failed:
        Integrations(Paths.create(tmp_path / "failed"), QueueRunner([(1, "", "bad")])).clone_agency()  # type: ignore[arg-type]
    assert failed.value.code == "NPB-302"


def test_agency_install_branches(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    paths = Paths.create(tmp_path / "builder")
    monkeypatch.setattr("newbie_project_builder.integrations.shutil.which", lambda name: None)
    with pytest.raises(BuilderError):
        Integrations(paths, QueueRunner()).install_core_agents()  # type: ignore[arg-type]

    monkeypatch.setattr("newbie_project_builder.integrations.shutil.which", lambda name: "/bin/bash")
    checkout = paths.integrations / "agency-agents"
    (checkout / ".git").mkdir(parents=True)
    assert Integrations(paths, QueueRunner([(0, "", ""), (0, "", "")])).install_core_agents()  # type: ignore[arg-type]
    with pytest.raises(BuilderError):
        Integrations(paths, QueueRunner([(1, "", "convert failed")])).install_core_agents()  # type: ignore[arg-type]
    with pytest.raises(BuilderError):
        Integrations(paths, QueueRunner([(0, "", ""), (1, "", "install failed")])).install_core_agents()  # type: ignore[arg-type]


def test_support_bundle_redacts_and_excludes_projects(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    paths = Paths.create(tmp_path / "builder")
    paths.ensure()
    private_home = tmp_path / "private-user-home"
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: private_home))
    (paths.logs / "one.log").write_text(
        f"token=secret-value\nPath: {private_home}/project",
        encoding="utf-8",
    )
    paths.state.write_text(json.dumps({"token": "private", "step": "x"}), encoding="utf-8")
    project = tmp_path / "project"
    project.mkdir()
    (project / "source.py").write_text("secret source", encoding="utf-8")
    host = Host(OSKind.LINUX, LinuxKind.APT, "Linux", "6", "x", "debian", "Debian", "13")
    archive = Support(paths, host).create(now=datetime(2026, 8, 12, tzinfo=UTC))
    names = members(archive)
    assert "README.txt" in names and "system-info.json" in names and "builder-state.json" in names
    assert not any("source.py" in name for name in names)
    import zipfile

    with zipfile.ZipFile(archive) as bundle:
        log_text = bundle.read(next(name for name in names if name.startswith("logs/"))).decode()
        state_text = bundle.read("builder-state.json").decode()
    assert "secret-value" not in log_text
    assert str(private_home) not in log_text
    assert "<HOME>" in log_text
    assert "private" not in state_text


def test_support_handles_invalid_state_and_log_limit(tmp_path: Path) -> None:
    paths = Paths.create(tmp_path / "builder")
    paths.ensure()
    for index in range(4):
        (paths.logs / f"{index}.log").write_text(str(index), encoding="utf-8")
    paths.state.write_text("token=secret-value", encoding="utf-8")
    host = Host(OSKind.WINDOWS, LinuxKind.NONE, "Windows", "11", "AMD64")
    archive = Support(paths, host).create(maximum_logs=2, now=datetime(2026, 8, 12, tzinfo=UTC))
    names = members(archive)
    assert len([name for name in names if name.startswith("logs/")]) == 2


def test_console_prompt_choose_confirm_and_phrase() -> None:
    answers = iter(["", "bad", "2", "maybe", "yes", "NO", "MATCH"])
    output: list[str] = []
    console = Console(input_func=lambda prompt: next(answers), output_func=output.append)
    assert console.prompt("Name", "Default") == "Default"
    assert console.choose("Choose", ["A", "B"]) == 1
    assert console.confirm("Continue?")
    assert not console.phrase("Explain", "MATCH")  # consumes NO
    assert console.phrase("Explain", "MATCH")
    assert any("Please enter" in line for line in output)
    assert any("Please type yes or no" in line for line in output)
    with pytest.raises(ValueError):
        console.choose("Nothing", [])


def test_console_confirm_defaults() -> None:
    yes = Console(input_func=lambda prompt: "", output_func=lambda line: None)
    no = Console(input_func=lambda prompt: "", output_func=lambda line: None)
    assert yes.confirm("Continue", default=True)
    assert not no.confirm("Continue", default=False)
