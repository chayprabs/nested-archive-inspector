from __future__ import annotations

import uuid
from pathlib import Path

from src.core.tree import build_tree_from_path, flatten_entries
from src.models import DiffChange, DiffResult


def diff_archives(left_path: Path, right_path: Path) -> DiffResult:
    job_id = str(uuid.uuid4())
    left = flatten_entries(build_tree_from_path(left_path, job_id, left_path.name).tree)
    right = flatten_entries(build_tree_from_path(right_path, job_id, right_path.name).tree)

    left_map = {entry.path: entry for entry in left if entry.path}
    right_map = {entry.path: entry for entry in right if entry.path}

    changes: list[DiffChange] = []
    added = removed = content_changed = metadata_changed = renamed = 0

    for path, entry in left_map.items():
        if path not in right_map:
            removed += 1
            changes.append(DiffChange(kind="removed", path=path, sizeBefore=entry.size))
            continue
        other = right_map[path]
        if entry.sha256 and other.sha256 and entry.sha256 != other.sha256:
            content_changed += 1
            changes.append(
                DiffChange(
                    kind="content_changed",
                    path=path,
                    sha256Before=entry.sha256,
                    sha256After=other.sha256,
                    sizeBefore=entry.size,
                    sizeAfter=other.size,
                )
            )
        elif entry.size != other.size or entry.mode != other.mode or entry.mtime != other.mtime:
            metadata_changed += 1
            changes.append(
                DiffChange(
                    kind="metadata_changed",
                    path=path,
                    sizeBefore=entry.size,
                    sizeAfter=other.size,
                )
            )

    for path, entry in right_map.items():
        if path not in left_map:
            added += 1
            changes.append(DiffChange(kind="added", path=path, sizeAfter=entry.size))

    return DiffResult(
        jobId=job_id,
        added=added,
        removed=removed,
        contentChanged=content_changed,
        metadataChanged=metadata_changed,
        renamed=renamed,
        changes=changes,
    )
