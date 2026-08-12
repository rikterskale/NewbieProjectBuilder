"""Read-only diagnostics for host, disk, network, and required tools."""

from __future__ import annotations

import shutil
import socket
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from newbie_project_builder.host import detect
from newbie_project_builder.models import Check, Host, OSKind, Tool


class DiskUsageLike(Protocol):
    @property
    def free(self) -> int: ...


def _disk_usage(path: Path) -> DiskUsageLike:
    return shutil.disk_usage(path)


class Preflight:
    def __init__(
        self,
        *,
        host: Host | None = None,
        which: Callable[[str], str | None] = shutil.which,
        disk_usage: Callable[[Path], DiskUsageLike] = _disk_usage,
        connect: Callable[..., socket.socket] = socket.create_connection,
    ) -> None:
        self.host = host or detect()
        self._which = which
        self._disk_usage = disk_usage
        self._connect = connect

    def operating_system(self) -> Check:
        return Check(
            "OS" if self.host.supported else "NPB-001",
            "Supported operating system",
            self.host.supported,
            f"Detected {self.host.display_name} ({self.host.machine}).",
            "Use diagnostics only or the manual guide." if not self.host.supported else "",
        )

    def disk(self, path: Path, minimum_gb: float = 2.0) -> Check:
        free_gb = self._disk_usage(path.expanduser()).free / (1024**3)
        passed = free_gb >= minimum_gb
        return Check(
            "DISK" if passed else "NPB-002",
            "Free disk space",
            passed,
            f"{free_gb:.2f} GB free at {path.expanduser()}.",
            "Free at least 2 GB and run diagnostics again." if not passed else "",
        )

    def internet(self, host: str = "github.com", port: int = 443) -> Check:
        try:
            connection = self._connect((host, port), timeout=3)
            connection.close()
        except OSError as exc:
            return Check(
                "NPB-003",
                "Internet connection",
                False,
                f"Could not reach {host}:{port}: {exc}",
                "Check network, VPN, proxy, and firewall settings.",
                required=False,
            )
        return Check(
            "NET",
            "Internet connection",
            True,
            f"Reached {host}:{port} over HTTPS.",
            required=False,
        )

    def _tool(self, key: str, name: str, command: str, *, required: bool) -> Tool:
        found = self._which(command)
        return Tool(key, name, command, found is not None, found or "", required=required)

    def tools(self) -> tuple[Tool, ...]:
        values = [
            Tool(
                "python",
                "Python",
                "python",
                sys.version_info >= (3, 11),
                sys.executable,
                ".".join(str(part) for part in sys.version_info[:3]),
                True,
            ),
            self._tool("git", "Git", "git", required=True),
            self._tool("gh", "GitHub CLI", "gh", required=False),
            self._tool("codex", "Codex CLI", "codex", required=False),
            self._tool("bash", "Bash", "bash", required=False),
        ]
        if self.host.os_kind is OSKind.WINDOWS:
            values.append(self._tool("winget", "Windows Package Manager", "winget", required=False))
            desktop_paths = (
                Path.home() / "AppData" / "Local" / "GitHubDesktop" / "GitHubDesktop.exe",
                Path("C:/Program Files/GitHub Desktop/GitHubDesktop.exe"),
            )
            desktop = next((item for item in desktop_paths if item.exists()), None)
            values.append(
                Tool(
                    "github_desktop",
                    "GitHub Desktop",
                    "GitHubDesktop.exe",
                    desktop is not None,
                    str(desktop or ""),
                    required=False,
                )
            )
        elif self.host.os_kind is OSKind.LINUX:
            values.append(self._tool("apt", "APT package manager", "apt-get", required=False))
        return tuple(values)

    def run(self, disk_path: Path) -> tuple[Check, ...]:
        checks = [self.operating_system(), self.disk(disk_path), self.internet()]
        for tool in self.tools():
            checks.append(
                Check(
                    tool.key.upper(),
                    tool.name,
                    tool.installed,
                    f"Installed at {tool.path or '<not found>'}"
                    + (f"; version {tool.version}" if tool.version else ""),
                    "Use guided setup to install or configure it." if not tool.installed else "",
                    required=tool.required,
                )
            )
        return tuple(checks)
