"""Verbose per-operation logs with mandatory redaction."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock

from newbie_project_builder.models import CommandResult, Paths
from newbie_project_builder.redaction import redact


class OperationLog:
    def __init__(
        self,
        paths: Paths,
        *,
        operation_id: str | None = None,
        now: datetime | None = None,
    ) -> None:
        paths.ensure()
        started = now or datetime.now(UTC)
        self.operation_id = operation_id or (
            f"NPB-{started:%Y%m%d-%H%M%S}-{secrets.token_hex(2).upper()}"
        )
        self.path = paths.logs / f"{started:%Y-%m-%d-%H%M%S}-{self.operation_id}.log"
        self._lock = Lock()
        self.message("Application start", f"Log file: {self.path}", result="STARTED")

    def _write(self, block: str) -> None:
        with self._lock, self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(redact(block).rstrip() + "\n")

    def message(self, step: str, message: str, *, result: str = "INFO") -> None:
        self._write(
            "\n".join(
                (
                    "=" * 72,
                    f"Timestamp: {datetime.now(UTC).astimezone().isoformat(timespec='milliseconds')}",
                    f"Operation ID: {self.operation_id}",
                    f"Step: {step}",
                    f"Result: {result}",
                    "Message:",
                    message or "<empty>",
                )
            )
        )

    def command(self, step: str, result: CommandResult, cwd: Path | None) -> None:
        outcome = "DRY-RUN" if result.dry_run else ("PASS" if result.ok else "FAIL")
        self._write(
            "\n".join(
                (
                    "=" * 72,
                    f"Timestamp: {datetime.now(UTC).astimezone().isoformat(timespec='milliseconds')}",
                    f"Operation ID: {self.operation_id}",
                    f"Step: {step}",
                    f"Started: {result.started_at.astimezone().isoformat(timespec='milliseconds')}",
                    f"Working directory: {cwd or Path.cwd()}",
                    f"Command: {' '.join(result.command)}",
                    f"Exit code: {result.exit_code}",
                    f"Duration: {result.duration_seconds:.3f} seconds",
                    f"Result: {outcome}",
                    "STDOUT:",
                    result.stdout or "<empty>",
                    "STDERR:",
                    result.stderr or "<empty>",
                )
            )
        )

    @staticmethod
    def latest(paths: Paths) -> Path | None:
        if not paths.logs.exists():
            return None
        candidates = sorted(paths.logs.glob("*.log"), key=lambda item: item.stat().st_mtime)
        return candidates[-1] if candidates else None
