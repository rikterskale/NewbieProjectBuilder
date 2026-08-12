from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from newbie_project_builder.backup import Backups
from newbie_project_builder.errors import BuilderError
from newbie_project_builder.models import (
    CommandResult,
    Paths,
    ProjectKind,
    ProjectOptions,
    Visibility,
    WorkflowState,
)
from newbie_project_builder.project import Generator, files_for, slugify
from newbie_project_builder.state import StateStore


class FakeLog:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str, str]] = []

    def message(self, step: str, message: str, *, result: str = "INFO") -> None:
        self.messages.append((step, message, result))


class FakeRunner:
    def __init__(self, *, dry_run: bool = False, exit_code: int = 0) -> None:
        self.dry_run = dry_run
        self.exit_code = exit_code
        self.commands: list[tuple[str, ...]] = []

    def run(self, command: tuple[str, ...], **kwargs: object) -> CommandResult:
        self.commands.append(tuple(command))
        return CommandResult(
            tuple(command),
            self.exit_code,
            "",
            "git error" if self.exit_code else "",
            0,
            datetime.now(UTC),
            self.dry_run,
        )


def options(tmp_path: Path, kind: ProjectKind = ProjectKind.GENERIC) -> ProjectOptions:
    return ProjectOptions("Weather Helper", "weather-helper", kind, "My family", Visibility.LOCAL_ONLY, tmp_path)


def test_state_store_round_trip_progress_failure_and_clear(tmp_path: Path) -> None:
    store = StateStore(tmp_path / "state.json")
    assert store.load() is None
    state = WorkflowState("OP-1", "setup", next_step="one")
    store.save(state)
    loaded = store.load()
    assert loaded is not None and loaded.operation_id == "OP-1"
    store.complete(state, "one", "two")
    store.complete(state, "one", "two")
    assert state.completed_steps == ["one"]
    assert state.last_error is None
    store.fail(state, "NPB-101", "one")
    assert store.load().last_error == "NPB-101"  # type: ignore[union-attr]
    store.clear()
    assert not store.path.exists()
    store.clear()


def test_backup_copy_write_same_replace_and_directory_error(tmp_path: Path) -> None:
    manager = Backups(tmp_path / "backups", now=datetime(2026, 8, 12, tzinfo=UTC))
    root = tmp_path / "project"
    source = root / "docs" / "file.txt"
    source.parent.mkdir(parents=True)
    source.write_text("old", encoding="utf-8")
    copied = manager.copy(source, root)
    assert copied is not None and copied.read_text(encoding="utf-8") == "old"
    assert manager.write(source, "old", project_root=root) is None
    with pytest.raises(BuilderError):
        manager.write(source, "new", project_root=root)
    replaced = manager.write(source, "new", project_root=root, replace=True)
    assert replaced is not None and replaced.read_text(encoding="utf-8") == "old"
    assert source.read_text(encoding="utf-8") == "new"
    assert manager.copy(root / "missing", root) is None
    with pytest.raises(BuilderError):
        manager.copy(source.parent, root)


def test_backup_external_relative_fallback(tmp_path: Path) -> None:
    manager = Backups(tmp_path / "backups", now=datetime(2026, 8, 12, tzinfo=UTC))
    external = tmp_path / "external.txt"
    external.write_text("value", encoding="utf-8")
    copied = manager.copy(external, tmp_path / "other")
    assert copied is not None and copied.name == "external.txt"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Weather Helper", "weather-helper"),
        ("  A__B  ", "a-b"),
        ("Résumé Project", "r-sum-project"),
    ],
)
def test_slugify(name: str, expected: str) -> None:
    assert slugify(name) == expected


@pytest.mark.parametrize("name", ["", "!!!", "CON", "LPT1"])
def test_slugify_rejects_invalid(name: str) -> None:
    with pytest.raises(BuilderError) as caught:
        slugify(name)
    assert caught.value.code == "NPB-402"


def test_files_for_all_project_kinds(tmp_path: Path) -> None:
    for kind in ProjectKind:
        generated = files_for(options(tmp_path, kind))
        assert "README.md" in generated
        assert "AGENTS.md" in generated
        assert all(content.endswith("\n") for content in generated.values())
        if kind is ProjectKind.PYTHON_CLI:
            assert "pyproject.toml" in generated
            assert "tests/test_cli.py" in generated
            assert "scripts/setup.ps1" in generated
            assert "scripts/setup.sh" in generated
            assert "scripts/check.ps1" in generated
            assert "scripts/check.sh" in generated
        else:
            assert "docs/NEXT_STEPS.md" in generated
        if kind is ProjectKind.SECURITY_TOOL:
            assert "docs/AUTHORIZATION_AND_SCOPE.md" in generated


def test_generator_preview_and_dry_run(tmp_path: Path) -> None:
    paths = Paths.create(tmp_path / "builder")
    log = FakeLog()
    runner = FakeRunner(dry_run=True)
    generator = Generator(paths, log, runner)  # type: ignore[arg-type]
    preview = generator.preview(options(tmp_path))
    assert preview == tuple(sorted(preview))
    result = generator.generate(options(tmp_path))
    assert result.dry_run
    assert not result.destination.exists()
    assert result.created
    assert log.messages[-1][2] == "PLANNED"


def test_generator_actual_nonempty_replace_and_backup(tmp_path: Path) -> None:
    paths = Paths.create(tmp_path / "builder")
    log = FakeLog()
    runner = FakeRunner()
    generator = Generator(paths, log, runner)  # type: ignore[arg-type]
    result = generator.generate(options(tmp_path), initialize_git=False)
    assert result.destination.is_dir()
    assert (result.destination / "README.md").is_file()
    assert not result.git_initialized
    with pytest.raises(BuilderError) as caught:
        generator.generate(options(tmp_path), initialize_git=False)
    assert caught.value.code == "NPB-401"
    readme = result.destination / "README.md"
    readme.write_text("changed", encoding="utf-8")
    replaced = generator.generate(options(tmp_path), initialize_git=False, replace=True)
    assert replaced.backups
    assert "Weather Helper" in readme.read_text(encoding="utf-8")


def test_generator_git_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    paths = Paths.create(tmp_path / "builder")
    log = FakeLog()
    runner = FakeRunner()
    monkeypatch.setattr("newbie_project_builder.project.shutil.which", lambda command: "/git")
    generator = Generator(paths, log, runner)  # type: ignore[arg-type]
    result = generator.generate(options(tmp_path))
    assert result.git_initialized
    assert runner.commands == [("git", "init", "-b", "main")]
    (result.destination / ".git").mkdir()
    second = generator.generate(options(tmp_path), replace=True)
    assert second.git_initialized
    assert runner.commands == [("git", "init", "-b", "main")]


def test_generator_no_git_and_failed_git(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    paths = Paths.create(tmp_path / "builder")
    log = FakeLog()
    monkeypatch.setattr("newbie_project_builder.project.shutil.which", lambda command: None)
    no_git = Generator(paths, log, FakeRunner())  # type: ignore[arg-type]
    assert not no_git.generate(options(tmp_path / "one")).git_initialized
    monkeypatch.setattr("newbie_project_builder.project.shutil.which", lambda command: "/git")
    failed = Generator(paths, log, FakeRunner(exit_code=1))  # type: ignore[arg-type]
    with pytest.raises(BuilderError) as caught:
        failed.generate(options(tmp_path / "two"))
    assert caught.value.code == "NPB-501"


def test_generator_refuses_credential_like_project_content(tmp_path: Path) -> None:
    paths = Paths.create(tmp_path / "builder")
    log = FakeLog()
    generator = Generator(paths, log, FakeRunner())  # type: ignore[arg-type]
    unsafe = ProjectOptions(
        "Unsafe Demo",
        "unsafe-demo",
        ProjectKind.PYTHON_CLI,
        "Only me",
        Visibility.LOCAL_ONLY,
        tmp_path,
        "token=actual-looking-secret",
    )

    with pytest.raises(BuilderError) as caught:
        generator.preview(unsafe)

    assert caught.value.code == "NPB-701"
    assert not unsafe.destination.exists()
