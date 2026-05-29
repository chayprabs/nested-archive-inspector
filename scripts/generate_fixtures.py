#!/usr/bin/env python3
"""Generate acceptance fixtures for ArchiveVet."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "apps" / "worker" / "tests" / "fixtures"
SAMPLES = ROOT / "apps" / "web" / "public" / "samples"


def write_zip(path: Path, entries: dict[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, payload in entries.items():
            archive.writestr(name, payload)
    path.write_bytes(buffer.getvalue())


def main() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    SAMPLES.mkdir(parents=True, exist_ok=True)

    safe = {f"file-{index}.txt": f"payload-{index}".encode() for index in range(5)}
    write_zip(FIXTURES / "safe-release.zip", safe)
    write_zip(SAMPLES / "safe-release.zip", safe)

    traversal = {
        "ok.txt": b"ok",
        "../../etc/passwd": b"bad",
    }
    write_zip(FIXTURES / "path-traversal.zip", traversal)
    write_zip(SAMPLES / "path-traversal.zip", traversal)

    nested_so = {
        "outer/readme.txt": b"nested",
        **{f"outer/lib/lib{n}.so": b"x" for n in range(12)},
    }
    write_zip(FIXTURES / "nested-so.zip", nested_so)
    write_zip(SAMPLES / "nested-so.zip", nested_so)

    manifest = {"expectedDiffChanges": 67}
    (FIXTURES / "diff-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote fixtures under {FIXTURES} and {SAMPLES}")


if __name__ == "__main__":
    main()
