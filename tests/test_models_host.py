from __future__ import annotations

from pathlib import Path

import pytest

from newbie_project_builder.host import default_home, detect, paths, read_os_release
from newbie_project_builder.models import (
    Host,
    LinuxKind,
    OSKind,
    Paths,
    ProjectKind,
    ProjectOptions,
    Visibility,
)


def test_paths_create_and_ensure(tmp_path: Path) -> None:
    value = Paths.create(tmp_path / "builder")
    assert value.logs == (tmp_path / "builder" / "logs").resolve()
    value.ensure()
    assert all(
        item.is_dir()
        for item in (value.home, value.logs, value.backups, value.support, value.integrations)
    )


def test_host_properties() -> None:
    windows = Host(OSKind.WINDOWS, LinuxKind.NONE, "Windows", "11", "AMD64")
    assert windows.supported
    assert windows.display_name == "Windows 11"
    linux = Host(OSKind.LINUX, LinuxKind.APT, "Linux", "6", "x86", "kali", "Kali", "2026")
    assert linux.supported
    assert linux.display_name == "Kali 2026"
    unsupported = Host(OSKind.LINUX, LinuxKind.OTHER, "Linux", "6", "x86")
    assert not unsupported.supported
    assert unsupported.display_name == "Linux"
    other = Host(OSKind.OTHER, LinuxKind.NONE, "Darwin", "25", "arm64")
    assert not other.supported
    assert other.display_name == "Darwin 25"


def test_read_os_release(tmp_path: Path) -> None:
    source = tmp_path / "os-release"
    source.write_text(
        '# comment\nID="ubuntu"\nNAME=Ubuntu\nINVALID\nEMPTY=\'value\'\n', encoding="utf-8"
    )
    assert read_os_release(source) == {
        "ID": "ubuntu",
        "NAME": "Ubuntu",
        "EMPTY": "value",
    }
    assert read_os_release(tmp_path / "missing") == {}


def test_detect_windows_linux_and_other(tmp_path: Path) -> None:
    windows = detect(system="Windows")
    assert windows.os_kind is OSKind.WINDOWS
    release = tmp_path / "os-release"
    release.write_text('ID=kali\nPRETTY_NAME="Kali Linux"\nVERSION_ID=2026\n', encoding="utf-8")
    linux = detect(system="Linux", os_release=release)
    assert linux.linux_kind is LinuxKind.APT
    assert linux.distro_id == "kali"
    release.write_text('ID=fedora\nID_LIKE="rhel"\n', encoding="utf-8")
    fedora = detect(system="Linux", os_release=release)
    assert fedora.linux_kind is LinuxKind.OTHER
    other = detect(system="Plan9")
    assert other.os_kind is OSKind.OTHER


def test_detect_does_not_assume_support_from_id_like(tmp_path: Path) -> None:
    release = tmp_path / "os-release"
    release.write_text('ID=custom\nID_LIKE="debian"\n', encoding="utf-8")
    assert detect(system="Linux", os_release=release).linux_kind is LinuxKind.OTHER


def test_default_home_and_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "profile"))
    windows = Host(OSKind.WINDOWS, LinuxKind.NONE, "Windows", "11", "AMD64")
    assert default_home(windows) == tmp_path / "profile" / "Documents" / "NewbieProjectBuilder"
    linux = Host(OSKind.LINUX, LinuxKind.APT, "Linux", "6", "x86")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "home"))
    assert default_home(linux) == tmp_path / "home" / "NewbieProjectBuilder"
    assert paths(tmp_path / "custom").home == (tmp_path / "custom").resolve()


def test_project_options_destination(tmp_path: Path) -> None:
    options = ProjectOptions(
        "Demo", "demo", ProjectKind.GENERIC, "Me", Visibility.LOCAL_ONLY, tmp_path
    )
    assert options.destination == tmp_path.resolve() / "demo"


def test_detect_does_not_guess_from_id_like(tmp_path: Path) -> None:
    release = tmp_path / "os-release"
    release.write_text(
        'ID=linuxmint\nID_LIKE="ubuntu debian"\nPRETTY_NAME="Linux Mint"\n',
        encoding="utf-8",
    )

    host = detect(system="Linux", os_release=release)

    assert host.linux_kind is LinuxKind.OTHER
    assert not host.supported
