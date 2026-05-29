from __future__ import annotations

import os
import re

from src.models import ArchiveEntry, SafetyFlag

_PATH_TRAVERSAL = re.compile(r"(^|[\\/])\.\.([\\/]|$)|^[a-zA-Z]:[\\/]|^/")
_COMPRESSION_RATIO_THRESHOLD = float(os.getenv("ARCHIVEVET_COMPRESSION_RATIO", "100"))
_AGGREGATE_RATIO_THRESHOLD = float(os.getenv("ARCHIVEVET_AGGREGATE_RATIO", "1000"))


def detect_path_traversal(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return bool(_PATH_TRAVERSAL.search(normalized))


def detect_symlink_escape(path: str, link_target: str | None) -> bool:
    if not link_target:
        return False
    target = link_target.replace("\\", "/")
    if target.startswith("/") or re.match(r"^[a-zA-Z]:/", target):
        return True
    combined = f"{path.rstrip('/')}/{target}".replace("\\", "/")
    parts: list[str] = []
    for segment in combined.split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if not parts:
                return True
            parts.pop()
            continue
        parts.append(segment)
    return any(part == ".." for part in parts)


def compression_ratio_flag(size: int, compressed_size: int) -> bool:
    if compressed_size <= 0 or size <= 0:
        return False
    return (size / compressed_size) > _COMPRESSION_RATIO_THRESHOLD


def aggregate_compression_flag(total_size: int, total_compressed: int) -> bool:
    if total_compressed <= 0 or total_size <= 0:
        return False
    return (total_size / total_compressed) > _AGGREGATE_RATIO_THRESHOLD


def flag_entry(entry: ArchiveEntry) -> list[SafetyFlag]:
    flags: list[SafetyFlag] = []
    if detect_path_traversal(entry.path):
        flags.append("path_traversal")
    if entry.isSymlink and detect_symlink_escape(entry.path, entry.linkTarget):
        flags.append("symlink_escape")
    if compression_ratio_flag(entry.size, entry.compressedSize):
        flags.append("high_compression_ratio")
    if entry.isEncrypted:
        flags.append("encrypted")
    return flags


def summarize_flags(entries: list[ArchiveEntry], depth: int, entry_count: int) -> list[SafetyFlag]:
    flags: set[SafetyFlag] = set()
    total_size = 0
    total_compressed = 0
    for entry in entries:
        total_size += entry.size
        total_compressed += entry.compressedSize or entry.size
        flags.update(entry.flags)
        if entry.children:
            child_flags = summarize_flags(entry.children, depth + 1, entry_count)
            flags.update(child_flags)

    if aggregate_compression_flag(total_size, total_compressed):
        flags.add("high_compression_ratio")
    if entry_count > int(os.getenv("ARCHIVEVET_MAX_ENTRIES_WARN", "100000")):
        flags.add("suspicious_file_count")
    if depth > int(os.getenv("ARCHIVEVET_MAX_DEPTH_WARN", "6")):
        flags.add("suspicious_depth")
    return sorted(flags)


def blocked_extract(flags: list[SafetyFlag]) -> bool:
    blocking = {"path_traversal", "symlink_escape", "high_compression_ratio"}
    return bool(blocking.intersection(flags))
