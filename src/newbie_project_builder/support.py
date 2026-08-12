"""Sanitized support bundles containing logs and system metadata only."""

from __future__ import annotations

import json
import platform
import sys
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from newbie_project_builder.models import Host, Paths
from newbie_project_builder.redaction import redact, redact_data


def _sanitize_text(text: str) -> str:
    sanitized = redact(text)
    home = str(Path.home())
    return sanitized.replace(home, "<HOME>") if home else sanitized


class Support:
    def __init__(self, paths: Paths, host: Host) -> None:
        self.paths = paths
        self.host = host

    def create(self, *, maximum_logs: int = 5, now: datetime | None = None) -> Path:
        self.paths.ensure()
        timestamp = now or datetime.now(UTC)
        destination = self.paths.support / f"npb-support-{timestamp:%Y%m%d-%H%M%S}.zip"
        with tempfile.TemporaryDirectory(prefix="npb-support-") as temporary:
            root = Path(temporary)
            logs_dir = root / "logs"
            logs_dir.mkdir()
            logs = []
            if self.paths.logs.exists():
                logs = sorted(
                    self.paths.logs.glob("*.log"),
                    key=lambda item: item.stat().st_mtime,
                    reverse=True,
                )[:maximum_logs]
            for source in logs:
                text = _sanitize_text(source.read_text(encoding="utf-8", errors="replace"))
                (logs_dir / source.name).write_text(text, encoding="utf-8")
            info = redact_data(
                {
                    "created_at": timestamp.isoformat(),
                    "host": self.host.display_name,
                    "machine": self.host.machine,
                    "python": sys.version,
                    "python_executable": _sanitize_text(sys.executable),
                    "platform": platform.platform(),
                    "included_logs": len(logs),
                    "excluded": [
                        "project source",
                        "user documents",
                        "browser data",
                        "environment variables",
                        "credentials",
                    ],
                }
            )
            (root / "system-info.json").write_text(
                json.dumps(info, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            if self.paths.state.exists():
                raw = self.paths.state.read_text(encoding="utf-8", errors="replace")
                try:
                    state = json.dumps(redact_data(json.loads(raw)), indent=2, sort_keys=True) + "\n"
                except json.JSONDecodeError:
                    state = _sanitize_text(raw)
                (root / "builder-state.json").write_text(_sanitize_text(state), encoding="utf-8")
            (root / "README.txt").write_text(
                "Sanitized Newbie Project Builder support bundle.\n"
                "Project source is not included. Review this archive before sharing.\n",
                encoding="utf-8",
            )
            with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for source in sorted(root.rglob("*")):
                    if source.is_file():
                        archive.write(source, source.relative_to(root))
        return destination


def members(path: Path) -> tuple[str, ...]:
    with zipfile.ZipFile(path) as archive:
        return tuple(sorted(archive.namelist()))
