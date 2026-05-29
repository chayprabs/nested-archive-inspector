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
_MAX_HASH_BYTES = int(os.getenv("ARCHIVEVET_MAX_HASH_BYTES", str(10 * 1024 * 1024)))

_ARCHIVE_EXTENSIONS = (
    ".zip",
    ".tar",
    ".tgz",
    ".tar.gz",
    ".tar.zst",
    ".tar.bz2",
    ".tar.xz",
    ".7z",
    ".rar",
    ".iso",
    ".dmg",
    ".cab",
    ".cpio",
    ".xar",
    ".deb",
)


def _guess_format(path: Path) -> str:
    suffixes = "".join(path.suffixes).lower()
    if suffixes.endswith(".tar.gz") or suffixes.endswith(".tgz"):
        return "tar.gz"
    if suffixes.endswith(".tar.zst"):
        return "tar.zst"
    if suffixes:
        return suffixes.lstrip(".")
    return "unknown"


def _guess_mime(path: str) -> str | None:
    lowered = path.lower()
    for ext in _ARCHIVE_EXTENSIONS:
        if lowered.endswith(ext):
            return f"application/x-archive{ext}"
    if lowered.endswith(".so"):
        return "application/x-sharedlib"
    if lowered.endswith(".txt"):
        return "text/plain"
    return None


def _entry_hash(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _read_entry_sha256(entry: object, size: int) -> str | None:
    if size <= 0 or size > _MAX_HASH_BYTES:
        return None
    try:
        payload = b"".join(entry.get_blocks())
    except Exception:
        return None
    return _entry_hash(payload)


def nest_flat_entries(flat: list[ArchiveEntry]) -> list[ArchiveEntry]:
    """Turn libarchive flat paths into a nested tree (F2)."""
    by_root: dict[str, list[ArchiveEntry]] = {}
    for entry in flat:
        normalized = entry.path.replace("\\", "/")
        parts = [part for part in normalized.split("/") if part]
        if not parts:
            continue
        by_root.setdefault(parts[0], []).append(entry)

    tree: list[ArchiveEntry] = []
    for top in sorted(by_root):
        group = by_root[top]
        singles = [entry for entry in group if entry.path.replace("\\", "/") == top]
        nested = [
            entry
            for entry in group
            if entry.path.replace("\\", "/") != top and "/" in entry.path.replace("\\", "/")
        ]

        if not nested and len(singles) == 1:
            tree.append(singles[0])
            continue

        children_flat: list[ArchiveEntry] = []
        for entry in group:
            normalized = entry.path.replace("\\", "/")
            if normalized == top:
                children_flat.append(entry)
                continue
            remainder = normalized[len(top) + 1 :]
            children_flat.append(entry.model_copy(update={"path": remainder}))

        tree.append(
            ArchiveEntry(
                path=top,
                isDir=True,
                mimeGuess=_guess_mime(top),
                children=nest_flat_entries(children_flat) or None,
            )
        )
    return tree


def build_tree_from_path(archive_path: Path, job_id: str, filename: str) -> InspectResult:
    flat: list[ArchiveEntry] = []
    entry_count = 0
    total_size = 0
    total_compressed = 0
    max_depth = 0
    warnings: list[str] = []

    with libarchive.file_reader(str(archive_path)) as archive:
        for entry in archive:
            if entry_count >= _MAX_ENTRIES:
                warnings.append("entry_cap_hit")
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

            sha256 = None
            if not is_dir and not is_symlink:
                sha256 = _read_entry_sha256(entry, size)

            node = ArchiveEntry(
                path=pathname,
                size=size,
                compressedSize=compressed,
                mtime=mtime,
                mode=int(entry.mode or 0),
                mimeGuess=_guess_mime(pathname),
                sha256=sha256,
                isDir=is_dir,
                isSymlink=is_symlink,
                linkTarget=link_target,
                isEncrypted=bool(getattr(entry, "encrypted", False)),
            )
            node.flags = flag_entry(node)
            flat.append(node)
            total_size += size
            total_compressed += compressed
            depth = pathname.count("/") + (1 if pathname else 0)
            max_depth = max(max_depth, depth)

    nested_tree = nest_flat_entries(flat)
    summary_flags = summarize_flags(flat, max_depth, entry_count)
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
        warnings=warnings,
    )
    return InspectResult(jobId=job_id, filename=filename, tree=nested_tree, summary=summary)


def flatten_entries(tree: list[ArchiveEntry]) -> list[ArchiveEntry]:
    flat: list[ArchiveEntry] = []

    def walk(nodes: list[ArchiveEntry], prefix: str = "") -> None:
        for node in nodes:
            path = node.path
            if prefix and not path.startswith(prefix):
                path = f"{prefix}/{path}".replace("//", "/")
            leaf = node.model_copy(update={"path": path})
            if node.children:
                walk(node.children, path)
            else:
                flat.append(leaf)

    walk(tree)
    return flat
