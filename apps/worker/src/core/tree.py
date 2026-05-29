from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

import libarchive

from src.core.flags import flag_entry, summarize_flags
from src.models import ArchiveEntry, InspectResult, InspectSummary

_MAX_DEPTH = int(os.getenv("MAX_ARCHIVE_DEPTH", os.getenv("ARCHIVEVET_MAX_DEPTH", "8")))
_MAX_ENTRIES = int(os.getenv("MAX_ENTRIES", os.getenv("ARCHIVEVET_MAX_ENTRIES", "200000")))


def _guess_format(path: Path) -> str:
    suffixes = "".join(path.suffixes).lower()
    if suffixes.endswith(".tar.gz") or suffixes.endswith(".tgz"):
        return "tar.gz"
    if suffixes.endswith(".tar.zst"):
        return "tar.zst"
    if suffixes:
        return suffixes.lstrip(".")
    return "unknown"


def _entry_hash(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def build_tree_from_path(archive_path: Path, job_id: str, filename: str) -> InspectResult:
    entries: list[ArchiveEntry] = []
    entry_count = 0
    total_size = 0
    total_compressed = 0
    max_depth = 0

    with libarchive.file_reader(str(archive_path)) as archive:
        for entry in archive:
            if entry_count >= _MAX_ENTRIES:
                break
            entry_count += 1
            pathname = entry.pathname or ""
            is_dir = entry.isdir
            is_symlink = entry.issym or entry.islnk
            link_target = entry.linkpath if is_symlink else None
            size = int(entry.size or 0)
            compressed = int(getattr(entry, "compressed_size", 0) or size)
            mtime = None
            if entry.mtime:
                mtime = datetime.fromtimestamp(entry.mtime, tz=timezone.utc).isoformat()

            node = ArchiveEntry(
                path=pathname,
                size=size,
                compressedSize=compressed,
                mtime=mtime,
                mode=int(entry.mode or 0),
                isDir=is_dir,
                isSymlink=is_symlink,
                linkTarget=link_target,
                isEncrypted=bool(getattr(entry, "encrypted", False)),
            )
            node.flags = flag_entry(node)
            entries.append(node)
            total_size += size
            total_compressed += compressed
            depth = pathname.count("/") + (1 if pathname else 0)
            max_depth = max(max_depth, depth)

    summary_flags = summarize_flags(entries, max_depth, entry_count)
    summary = InspectSummary(
        entryCount=entry_count,
        totalUncompressedBytes=total_size,
        totalCompressedBytes=total_compressed,
        maxDepth=max_depth,
        formatGuess=_guess_format(archive_path),
        flags=summary_flags,
        blockedExtract=any(
            flag in summary_flags
            for flag in ("path_traversal", "symlink_escape", "high_compression_ratio")
        ),
    )
    return InspectResult(jobId=job_id, filename=filename, tree=entries, summary=summary)


def flatten_entries(tree: list[ArchiveEntry]) -> list[ArchiveEntry]:
    flat: list[ArchiveEntry] = []

    def walk(nodes: list[ArchiveEntry]) -> None:
        for node in nodes:
            flat.append(node)
            if node.children:
                walk(node.children)

    walk(tree)
    return flat
