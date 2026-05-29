from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from src.core.tree import build_tree_from_path


def _write_zip(path: Path, entries: dict[str, bytes]) -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in entries.items():
            archive.writestr(name, payload)
    path.write_bytes(buffer.getvalue())


@pytest.fixture()
def sample_zip(tmp_path: Path) -> Path:
    target = tmp_path / "sample.zip"
    _write_zip(
        target,
        {
            "readme.txt": b"hello",
            "lib/libfoo.so": b"so-content",
            "lib/libbar.so": b"so-content-2",
        },
    )
    return target


def test_build_tree_from_zip(sample_zip: Path):
    result = build_tree_from_path(sample_zip, "job-1", sample_zip.name)
    assert result.summary.entryCount == 3
    assert result.summary.formatGuess.endswith("zip")
    paths = {entry.path for entry in result.tree}
    assert "readme.txt" in paths
    assert "lib/libfoo.so" in paths
