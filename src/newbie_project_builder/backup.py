"""Timestamped file backups before approved replacement."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

from newbie_project_builder.errors import BuilderError


class Backups:
    def __init__(self, root: Path, *, now: datetime | None = None) -> None:
        timestamp = now or datetime.now(UTC)
        self.session = root / f"{timestamp:%Y-%m-%d-%H%M%S}"

    def copy(self, source: Path, relative_to: Path) -> Path | None:
        if not source.exists():
            return None
        if source.is_dir():
            raise BuilderError("NPB-401", f"Expected a file, found a directory: {source}")
        try:
            relative = source.resolve().relative_to(relative_to.resolve())
        except ValueError:
            relative = Path(source.name)
        destination = self.session / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return destination

    def write(
        self,
        destination: Path,
        content: str,
        *,
        project_root: Path,
        replace: bool = False,
    ) -> Path | None:
        backup = None
        if destination.exists():
            current = destination.read_text(encoding="utf-8", errors="replace")
            if current == content:
                return None
            if not replace:
                raise BuilderError("NPB-401", f"Existing file differs: {destination}")
            backup = self.copy(destination, project_root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".npb.tmp")
        temporary.write_text(content, encoding="utf-8", newline="\n")
        temporary.replace(destination)
        return backup
