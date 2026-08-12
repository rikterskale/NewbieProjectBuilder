from __future__ import annotations

import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from newbie_project_builder.commands import Runner
from newbie_project_builder.errors import BuilderError
from newbie_project_builder.models import Paths
from newbie_project_builder.technical_logging import OperationLog


def make_log(tmp_path: Path, operation_id: str = "NPB-TEST") -> tuple[Paths, OperationLog]:
    value = Paths.create(tmp_path / "home")
    log = OperationLog(value, operation_id=operation_id, now=datetime(2026, 8, 12, tzinfo=UTC))
    return value, log


def test_operation_log_redacts_messages_and_finds_latest(tmp_path: Path) -> None:
    paths, log = make_log(tmp_path)
    fake_github_token = "gh" + "p_" + "abcdefghijklmnopqrstuvwxyz123456"
    log.message("Secret test", f"token={fake_github_token}", result="PASS")
    text = log.path.read_text(encoding="utf-8")
    assert "abcdefghijklmnopqrstuvwxyz123456" not in text
    assert "<REDACTED>" in text
    assert OperationLog.latest(paths) == log.path
    empty = Paths.create(tmp_path / "empty")
    assert OperationLog.latest(empty) is None


def test_runner_dry_run(tmp_path: Path) -> None:
    _paths, log = make_log(tmp_path)
    result = Runner(log, dry_run=True).run(("thing", "--flag"), step="Preview")
    assert result.ok and result.dry_run
    assert result.stdout == "DRY RUN: thing --flag"
    assert "DRY-RUN" in log.path.read_text(encoding="utf-8")


def test_runner_executes_and_redacts_output(tmp_path: Path) -> None:
    _paths, log = make_log(tmp_path)
    result = Runner(log).run(
        (sys.executable, "-c", "print('password=hunter2')"), step="Run Python"
    )
    assert result.ok
    assert result.stdout == "password=<REDACTED>\n"
    assert "hunter2" not in log.path.read_text(encoding="utf-8")


def test_runner_nonzero_result_is_returned(tmp_path: Path) -> None:
    _paths, log = make_log(tmp_path)
    result = Runner(log).run(
        (sys.executable, "-c", "import sys; print('bad', file=sys.stderr); sys.exit(3)"),
        step="Fail",
    )
    assert result.exit_code == 3
    assert result.stderr == "bad\n"


def test_runner_file_not_found(tmp_path: Path) -> None:
    _paths, log = make_log(tmp_path)
    with pytest.raises(BuilderError) as caught:
        Runner(log).run(("definitely-missing-npb-command",), step="Missing", error_code="NPB-101")
    assert caught.value.code == "NPB-101"
    assert "Command not found" in caught.value.details


def test_runner_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _paths, log = make_log(tmp_path)

    def timeout(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(args[0], 1, output=b"partial", stderr=b"token=secret")

    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(BuilderError) as caught:
        Runner(log).run(("slow",), step="Timeout", timeout=1, error_code="NPB-901")
    assert caught.value.code == "NPB-901"
    text = log.path.read_text(encoding="utf-8")
    assert "secret" not in text
    assert "partial" in text


def test_runner_passes_input_cwd_and_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _paths, log = make_log(tmp_path)
    captured: dict[str, object] = {}

    def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        captured.update(kwargs)
        return subprocess.CompletedProcess(args[0], 0, "ok", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = Runner(log).run(
        ("program",),
        step="Options",
        cwd=tmp_path,
        input_text="hello",
        env={"SAFE": "yes"},
    )
    assert result.ok
    assert captured["cwd"] == tmp_path
    assert captured["input"] == "hello"
    assert isinstance(captured["env"], dict)
    assert captured["env"]["SAFE"] == "yes"  # type: ignore[index]
    assert "PATH" in captured["env"]  # type: ignore[operator]


def test_runner_can_hide_private_arguments_and_output(tmp_path: Path) -> None:
    _paths, log = make_log(tmp_path)
    private_value = "private@example.test"
    result = Runner(log).run(
        (sys.executable, "-c", f"print({private_value!r})"),
        step="Private operation",
        display_command=(sys.executable, "-c", "<PRIVATE-INPUT>"),
        log_output=False,
    )
    assert result.stdout.strip() == private_value
    text = log.path.read_text(encoding="utf-8")
    assert private_value not in text
    assert "<PRIVATE-INPUT>" in text
    assert "<OMITTED FOR PRIVACY>" in text
