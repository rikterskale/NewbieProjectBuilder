"""Atomic progress state for resume after interruption."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from newbie_project_builder.models import WorkflowState
from newbie_project_builder.redaction import redact_data


class StateStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> WorkflowState | None:
        if not self.path.exists():
            return None
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return WorkflowState(
            operation_id=str(data["operation_id"]),
            workflow=str(data["workflow"]),
            completed_steps=[str(item) for item in data.get("completed_steps", [])],
            next_step=str(data.get("next_step", "")),
            last_error=str(data["last_error"]) if data.get("last_error") is not None else None,
            updated_at=str(data.get("updated_at", "")),
        )

    def save(self, state: WorkflowState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        state.updated_at = datetime.now(UTC).isoformat(timespec="seconds")
        text = json.dumps(redact_data(asdict(state)), indent=2, sort_keys=True) + "\n"
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(self.path)

    def complete(self, state: WorkflowState, step: str, next_step: str = "") -> None:
        if step not in state.completed_steps:
            state.completed_steps.append(step)
        state.next_step = next_step
        state.last_error = None
        self.save(state)

    def fail(self, state: WorkflowState, code: str, next_step: str = "") -> None:
        state.last_error = code
        state.next_step = next_step
        self.save(state)

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()
