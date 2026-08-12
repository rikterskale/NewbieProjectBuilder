"""Safe subprocess execution with complete capture and no shell interpolation."""

from __future__ import annotations

import os
import subprocess
import time
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from newbie_project_builder.errors import BuilderError
from newbie_project_builder.models import CommandResult
from newbie_project_builder.redaction import redact
from newbie_project_builder.technical_logging import OperationLog


class Runner:
    def __init__(self, log: OperationLog, *, dry_run: bool = False) -> None:
        self.log = log
        self.dry_run = dry_run

    def run(
        self,
        command: Sequence[str],
        *,
        step: str,
        cwd: Path | None = None,
        timeout: float = 300,
        input_text: str | None = None,
        env: Mapping[str, str] | None = None,
        error_code: str = "NPB-901",
        display_command: Sequence[str] | None = None,
        log_output: bool = True,
    ) -> CommandResult:
        args = tuple(str(value) for value in command)
        display_args = (
            tuple(str(value) for value in display_command)
            if display_command is not None
            else args
        )
        started = datetime.now(UTC)
        if self.dry_run:
            result = CommandResult(
                args,
                0,
                f"DRY RUN: {' '.join(display_args)}",
                "",
                0.0,
                started,
                True,
            )
            self.log.command(step, replace(result, command=display_args), cwd)
            return result

        before = time.monotonic()
        effective_env = None if env is None else {**os.environ, **dict(env)}
        try:
            completed = subprocess.run(
                args,
                cwd=cwd,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                env=effective_env,
            )
        except FileNotFoundError as exc:
            result = CommandResult(
                args,
                127,
                "",
                str(exc),
                time.monotonic() - before,
                started,
            )
            self.log.command(step, replace(result, command=display_args), cwd)
            raise BuilderError(error_code, f"Command not found: {args[0]}") from exc
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            result = CommandResult(
                args,
                124,
                redact(stdout),
                redact(stderr or f"Command timed out after {timeout} seconds."),
                time.monotonic() - before,
                started,
            )
            logged = replace(
                result,
                command=display_args,
                stdout=result.stdout if log_output else "<OMITTED FOR PRIVACY>",
                stderr=result.stderr if log_output else "<OMITTED FOR PRIVACY>",
            )
            self.log.command(step, logged, cwd)
            raise BuilderError(error_code, result.stderr) from exc

        result = CommandResult(
            args,
            completed.returncode,
            redact(completed.stdout),
            redact(completed.stderr),
            time.monotonic() - before,
            started,
        )
        logged = replace(
            result,
            command=display_args,
            stdout=result.stdout if log_output else "<OMITTED FOR PRIVACY>",
            stderr=result.stderr if log_output else "<OMITTED FOR PRIVACY>",
        )
        self.log.command(step, logged, cwd)
        return result
