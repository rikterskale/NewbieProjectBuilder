"""One-time, checksum-validated repository bootstrap.

This file and the payload chunks are deleted before the implementation commit.
The two repairs below correct characters that were proven missing during the
GitHub contents-API transfer. Full-payload and ZIP checksums remain the final
authority; extraction stops if any other byte differs.
"""

from __future__ import annotations

import base64
import hashlib
import os
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

EXPECTED_PARTS = 9
EXPECTED_PART_LENGTHS = (14000, 14000, 14000, 14000, 14000, 14000, 14000, 14000, 9924)
EXPECTED_BASE64_SHA256 = "7618afc19a8429d8e4e53f4efaae81ca43a4b1c40009f8ab008345ac72898eba"
EXPECTED_ZIP_SHA256 = "9528a0fad02224c67cdd887caa5a8cd7914b3a1b514f830a2e848c7abe4eb2d2"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_target(root: Path, archive_name: str) -> Path:
    relative = PurePosixPath(archive_name)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise RuntimeError(f"Unsafe archive path: {archive_name!r}")
    target = (root / Path(*relative.parts)).resolve()
    if not target.is_relative_to(root.resolve()):
        raise RuntimeError(f"Archive path escapes repository: {archive_name!r}")
    return target


def repaired_part(index: int, text: str) -> str:
    """Restore only the two omissions identified by exact blob comparison."""

    if index == 6 and len(text) == 13999:
        text = text[:1594] + "W" + text[1594:]
    elif index == 8 and len(text) == 9920:
        text = text[:5349] + "AAAA" + text[5349:]

    expected_length = EXPECTED_PART_LENGTHS[index]
    if len(text) != expected_length:
        raise RuntimeError(
            f"Unexpected length for payload part {index:02d}: "
            f"expected {expected_length}, received {len(text)}"
        )
    return text


def extract_archive(root: Path, archive_bytes: bytes) -> int:
    extracted = 0
    with tempfile.NamedTemporaryFile(suffix=".zip") as temporary:
        temporary.write(archive_bytes)
        temporary.flush()
        with zipfile.ZipFile(temporary.name) as archive:
            for info in archive.infolist():
                target = safe_target(root, info.filename)
                unix_mode = (info.external_attr >> 16) & 0o177777
                if stat.S_ISLNK(unix_mode):
                    raise RuntimeError(f"Symbolic links are not allowed: {info.filename!r}")
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(info))
                if unix_mode & 0o111:
                    os.chmod(target, target.stat().st_mode | 0o111)
                extracted += 1
    return extracted


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    bootstrap = root / ".bootstrap"
    paths = [bootstrap / f"payload.part{index:02d}" for index in range(EXPECTED_PARTS)]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise RuntimeError(f"Missing payload parts: {missing}")

    part_text = [
        repaired_part(index, path.read_text(encoding="ascii"))
        for index, path in enumerate(paths)
    ]
    encoded = "".join(part_text).encode("ascii")
    encoded_hash = sha256(encoded)
    if encoded_hash != EXPECTED_BASE64_SHA256:
        raise RuntimeError(
            "Base64 payload checksum mismatch: "
            f"expected {EXPECTED_BASE64_SHA256}, received {encoded_hash}"
        )

    archive_bytes = base64.b64decode(encoded, validate=True)
    archive_hash = sha256(archive_bytes)
    if archive_hash != EXPECTED_ZIP_SHA256:
        raise RuntimeError(
            "ZIP payload checksum mismatch: "
            f"expected {EXPECTED_ZIP_SHA256}, received {archive_hash}"
        )

    extracted = extract_archive(root, archive_bytes)
    shutil.rmtree(bootstrap)
    print(f"Verified and extracted {extracted} repository files.")


if __name__ == "__main__":
    main()
