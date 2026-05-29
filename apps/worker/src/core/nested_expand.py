from __future__ import annotations

import tempfile
from pathlib import Path

import libarchive

from src.core.formats import detect_format
from src.core.inspect_dispatch import inspect_archive_file
from src.core.tree import _ARCHIVE_EXTENSIONS
from src.models import ArchiveEntry


def _is_nested_archive_path(path: str) -> bool:
    lowered = path.lower()
    return any(lowered.endswith(ext) for ext in _ARCHIVE_EXTENSIONS)


def mark_lazy_nested_archives(tree: list[ArchiveEntry]) -> None:
    """Mark inner archive leaves as expandable without loading them (F2.3)."""

    def walk(nodes: list[ArchiveEntry]) -> None:
        for node in nodes:
            if node.children:
                walk(node.children)
            elif _is_nested_archive_path(node.path) and not node.isDir:
                node.isDir = True
                node.children = None
                node.mimeGuess = node.mimeGuess or f"application/x-archive"

    walk(tree)


def expand_nested_entry(archive_path: Path, member_path: str, job_id: str) -> list[ArchiveEntry]:
    normalized = member_path.replace("\\", "/").lstrip("/")
    with libarchive.file_reader(str(archive_path)) as archive:
        for entry in archive:
            if (entry.pathname or "").replace("\\", "/").lstrip("/") != normalized:
                continue
            if entry.isdir:
                return []
            payload = b"".join(entry.get_blocks())
            suffix = Path(normalized).suffix or ".bin"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
                handle.write(payload)
                inner_path = Path(handle.name)
            try:
                inspection = inspect_archive_file(inner_path, job_id, Path(normalized).name)
                return inspection.tree
            finally:
                inner_path.unlink(missing_ok=True)
    return []
