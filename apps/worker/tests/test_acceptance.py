from __future__ import annotations

import json
from pathlib import Path

import pytest

libarchive = pytest.importorskip("libarchive")

from src.core.diff import diff_archives
from src.core.tree import build_tree_from_path, flatten_entries

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST = json.loads((FIXTURES / "acceptance-manifest.json").read_text(encoding="utf-8"))


def test_a3_release_diff_has_67_changes():
    left = FIXTURES / "release-1.2.0.tar.gz"
    right = FIXTURES / "release-1.3.0.tar.gz"
    result = diff_archives(left, right)
    total = (
        result.added
        + result.removed
        + result.contentChanged
        + result.metadataChanged
        + result.renamed
    )
    assert total == MANIFEST["expectedTotalChanges"] == 67
    assert result.added == MANIFEST["added"]
    assert result.removed == MANIFEST["removed"]
    assert result.contentChanged == MANIFEST["contentChanged"]


def test_a5_nested_release_has_twelve_so_entries():
    archive = FIXTURES / "nested-release.tar.gz"
    inspection = build_tree_from_path(archive, "job-a5", archive.name)
    flat = flatten_entries(inspection.tree)
    so_paths = [entry.path for entry in flat if entry.path.endswith(".so")]
    assert len(so_paths) == MANIFEST["nestedSoExtractCount"] == 12


def test_tree_is_nested_not_only_flat_leaves():
    archive = FIXTURES / "nested-release.tar.gz"
    inspection = build_tree_from_path(archive, "job-tree", archive.name)
    assert any(entry.isDir and entry.children for entry in inspection.tree)
