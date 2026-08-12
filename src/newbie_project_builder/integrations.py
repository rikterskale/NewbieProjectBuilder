"""Guided checks for Codex, Superpowers, and Agency Agents."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from newbie_project_builder.commands import Runner
from newbie_project_builder.errors import BuilderError
from newbie_project_builder.models import Paths

CORE_AGENTS = (
    "product-manager",
    "software-architect",
    "code-reviewer",
    "test-automation-engineer",
    "appsec-engineer",
    "devops-automator",
    "technical-writer",
    "reality-checker",
)


@dataclass(frozen=True, slots=True)
class Integration:
    name: str
    available: bool
    details: str
    next_action: str


class Integrations:
    AGENCY_URL = "https://github.com/msitarzewski/agency-agents.git"

    def __init__(self, paths: Paths, runner: Runner) -> None:
        self.paths = paths
        self.runner = runner

    def statuses(self) -> tuple[Integration, ...]:
        codex = shutil.which("codex")
        plugin_candidates = (
            Path.home() / ".codex" / "plugins" / "superpowers",
            Path.home() / ".codex" / "skills" / "using-superpowers",
        )
        superpowers = next((item for item in plugin_candidates if item.exists()), None)
        agent_dir = Path.home() / ".codex" / "agents"
        installed = [name for name in CORE_AGENTS if (agent_dir / f"{name}.toml").exists()]
        return (
            Integration(
                "Codex",
                codex is not None,
                f"Executable: {codex or '<not found on PATH>'}",
                "Install Codex from the official OpenAI source." if not codex else "Open Codex.",
            ),
            Integration(
                "Superpowers",
                superpowers is not None,
                (
                    f"Possible marker: {superpowers}"
                    if superpowers
                    else "No filesystem marker found; Codex is the source of truth."
                ),
                "Open Codex Plugins, install Superpowers, then verify in a fresh session.",
            ),
            Integration(
                "Agency Agents core roster",
                len(installed) == len(CORE_AGENTS),
                f"Detected {len(installed)} of {len(CORE_AGENTS)} expected Codex agent files.",
                "Use the official Agency Agents app or optional guided installation.",
            ),
        )

    def clone_agency(self) -> Path:
        destination = self.paths.integrations / "agency-agents"
        if destination.exists():
            if (destination / ".git").exists():
                self.runner.log.message(
                    "Prepare Agency Agents",
                    f"Using existing builder-owned checkout at {destination}; no reset was run.",
                    result="SKIPPED",
                )
                return destination
            raise BuilderError("NPB-302", f"Not a Git checkout: {destination}")
        result = self.runner.run(
            ("git", "clone", "--depth", "1", self.AGENCY_URL, str(destination)),
            step="Clone official Agency Agents repository",
            timeout=900,
            error_code="NPB-302",
        )
        if not result.ok:
            raise BuilderError("NPB-302", result.stderr or result.stdout)
        return destination

    def install_core_agents(self) -> bool:
        if not shutil.which("bash"):
            raise BuilderError(
                "NPB-302",
                "Bash is unavailable. On Windows, use the official Agency Agents desktop app.",
            )
        checkout = self.clone_agency()
        converted = self.runner.run(
            ("bash", "scripts/convert.sh", "--tool", "codex"),
            step="Convert Agency Agents for Codex",
            cwd=checkout,
            timeout=900,
            error_code="NPB-302",
        )
        if not converted.ok:
            raise BuilderError("NPB-302", converted.stderr or converted.stdout)
        installed = self.runner.run(
            (
                "bash",
                "scripts/install.sh",
                "--tool",
                "codex",
                "--agent",
                ",".join(CORE_AGENTS),
            ),
            step="Install Agency Agents core roster",
            cwd=checkout,
            timeout=900,
            error_code="NPB-302",
        )
        if not installed.ok:
            raise BuilderError("NPB-302", installed.stderr or installed.stdout)
        return True
