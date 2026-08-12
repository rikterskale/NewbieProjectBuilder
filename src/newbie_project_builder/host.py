"""Operating-system detection and visible per-user path defaults."""

from __future__ import annotations

import os
import platform
from pathlib import Path

from newbie_project_builder.models import Host, LinuxKind, OSKind, Paths

_APT_IDS = frozenset({"ubuntu", "debian", "kali"})


def read_os_release(path: Path = Path("/etc/os-release")) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value.strip().strip('"').strip("'")
    return values


def detect(*, system: str | None = None, os_release: Path | None = None) -> Host:
    system_name = system or platform.system()
    release = platform.release()
    machine = platform.machine()
    if system_name.lower() == "windows":
        return Host(OSKind.WINDOWS, LinuxKind.NONE, system_name, release, machine)
    if system_name.lower() == "linux":
        values = read_os_release(os_release or Path("/etc/os-release"))
        distro_id = values.get("ID", "").lower()
        linux_kind = LinuxKind.APT if distro_id in _APT_IDS else LinuxKind.OTHER
        return Host(
            OSKind.LINUX,
            linux_kind,
            system_name,
            release,
            machine,
            distro_id,
            values.get("PRETTY_NAME") or values.get("NAME", ""),
            values.get("VERSION_ID", ""),
        )
    return Host(OSKind.OTHER, LinuxKind.NONE, system_name, release, machine)


def default_home(host: Host | None = None) -> Path:
    info = host or detect()
    if info.os_kind is OSKind.WINDOWS:
        profile = Path(os.environ.get("USERPROFILE", str(Path.home())))
        return profile / "Documents" / "NewbieProjectBuilder"
    return Path.home() / "NewbieProjectBuilder"


def paths(home: Path | None = None) -> Paths:
    return Paths.create(home or default_home())
