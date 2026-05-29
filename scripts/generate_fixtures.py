#!/usr/bin/env python3
"""Generate acceptance fixtures for ArchiveVet."""

from __future__ import annotations

import io
import json
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "apps" / "worker" / "tests" / "fixtures"
SAMPLES = ROOT / "apps" / "web" / "public" / "samples"
ADVERSARIAL = FIXTURES / "adversarial"


def write_zip(path: Path, entries: dict[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, payload in entries.items():
            archive.writestr(name, payload)
    path.write_bytes(buffer.getvalue())


def write_targz(path: Path, entries: dict[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for name, payload in entries.items():
            info = tarfile.TarInfo(name=name)
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))
    path.write_bytes(buffer.getvalue())


def _release_old() -> dict[str, bytes]:
    entries: dict[str, bytes] = {}
    for index in range(25):
        entries[f"common/changed_{index}.txt"] = f"release-1.2.0-{index}".encode()
    for index in range(20):
        entries[f"old/only_{index}.txt"] = b"removed-in-1.3.0"
    for index in range(10):
        entries[f"shared/stable_{index}.txt"] = b"unchanged"
    return entries


def _release_new() -> dict[str, bytes]:
    entries: dict[str, bytes] = {}
    for index in range(25):
        entries[f"common/changed_{index}.txt"] = f"release-1.3.0-{index}".encode()
    for index in range(22):
        entries[f"new/only_{index}.txt"] = b"added-in-1.3.0"
    for index in range(10):
        entries[f"shared/stable_{index}.txt"] = b"unchanged"
    return entries


def _nested_release_so() -> dict[str, bytes]:
    entries: dict[str, bytes] = {"README": b"nested release sample"}
    for index in range(12):
        entries[f"payload/vendor/lib/plugin_{index:02d}.so"] = f"so-{index}".encode()
    return entries


def write_encrypted_7z(path: Path, password: str = "demo") -> None:
    import py7zr

    path.parent.mkdir(parents=True, exist_ok=True)
    with py7zr.SevenZipFile(path, "w", password=password) as archive:
        archive.writestr("secret.txt", "encrypted-content")


def main() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    SAMPLES.mkdir(parents=True, exist_ok=True)
    ADVERSARIAL.mkdir(parents=True, exist_ok=True)

    safe = {f"file-{index}.txt": f"payload-{index}".encode() for index in range(5)}
    write_zip(FIXTURES / "safe-release.zip", safe)
    write_zip(SAMPLES / "safe-release.zip", safe)

    traversal = {"ok.txt": b"ok", "../../etc/passwd": b"bad"}
    write_zip(FIXTURES / "path-traversal.zip", traversal)
    write_zip(SAMPLES / "path-traversal.zip", traversal)
    write_zip(ADVERSARIAL / "path-traversal.zip", traversal)

    write_targz(FIXTURES / "release-1.2.0.tar.gz", _release_old())
    write_targz(FIXTURES / "release-1.3.0.tar.gz", _release_new())
    write_targz(SAMPLES / "release-1.2.0.tar.gz", _release_old())
    write_targz(SAMPLES / "release-1.3.0.tar.gz", _release_new())

    nested_so = _nested_release_so()
    write_targz(FIXTURES / "nested-release.tar.gz", nested_so)
    write_targz(SAMPLES / "nested-release.tar.gz", nested_so)

    write_encrypted_7z(FIXTURES / "encrypted.7z")
    write_encrypted_7z(SAMPLES / "encrypted.7z")

    inner = {"inner/hello.txt": b"nested-inner"}
    inner_buf = io.BytesIO()
    with zipfile.ZipFile(inner_buf, "w") as inner_zip:
        for name, payload in inner.items():
            inner_zip.writestr(name, payload)
    outer = {"bundle.zip": inner_buf.getvalue()}
    write_zip(FIXTURES / "nested-bundle.zip", outer)
    write_zip(SAMPLES / "nested-bundle.zip", outer)

    manifest = {
        "expectedTotalChanges": 67,
        "added": 22,
        "removed": 20,
        "contentChanged": 25,
        "metadataChanged": 0,
        "renamed": 0,
        "nestedSoExtractCount": 12,
    }
    (FIXTURES / "acceptance-manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(f"Wrote fixtures under {FIXTURES} and {SAMPLES}")


if __name__ == "__main__":
    main()
