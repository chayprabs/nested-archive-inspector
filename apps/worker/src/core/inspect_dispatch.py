from __future__ import annotations

from pathlib import Path

from src.core.formats import detect_format
from src.core.nested_expand import mark_lazy_nested_archives
from src.core.sevenzip import ArchivePasswordError, build_tree_from_7z
from src.core.tree import build_tree_from_path
from src.models import InspectResult


def inspect_archive_file(
    archive_path: Path,
    job_id: str,
    filename: str,
    password: str | None = None,
) -> InspectResult:
    if detect_format(archive_path) == "7z":
        result = build_tree_from_7z(archive_path, job_id, filename, password)
    else:
        result = build_tree_from_path(archive_path, job_id, filename)
        mark_lazy_nested_archives(result.tree)
    return result


__all__ = ["ArchivePasswordError", "inspect_archive_file"]
