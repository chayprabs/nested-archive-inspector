from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import py7zr
from py7zr.exceptions import Bad7zFile, PasswordRequired, Py7zrError

from src.core.flags import flag_entry, summarize_flags
from src.core.formats import detect_format
from src.core.tree import nest_flat_entries
from src.models import ArchiveEntry, InspectResult, InspectSummary

_PASSWORD_INVALID = "401_ARCHIVE_PASSWORD_INVALID"
_PASSWORD_REQUIRED = "401_ARCHIVE_PASSWORD_REQUIRED"


class ArchivePasswordError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def build_tree_from_7z(
    archive_path: Path, job_id: str, filename: str, password: str | None
) -> InspectResult:
    flat: list[ArchiveEntry] = []
    entry_count = 0
    total_size = 0
    encrypted_seen = False

    try:
        with py7zr.SevenZipFile(archive_path, mode="r", password=password) as archive:
            for entry in archive.list():
                entry_count += 1
                pathname = entry.filename
                is_dir = entry.is_directory
                size = int(entry.uncompressed or 0)
                mtime = None
                if entry.lastwritetime:
                    mtime = datetime.fromtimestamp(
                        entry.lastwritetime.timestamp(), tz=timezone.utc
                    ).isoformat()
                if entry.encrypted:
                    encrypted_seen = True
                node = ArchiveEntry(
                    path=pathname,
                    size=size,
                    compressedSize=size,
                    mtime=mtime,
                    mode=0o644,
                    isDir=is_dir,
                    isEncrypted=bool(entry.encrypted),
                )
                node.flags = flag_entry(node)
                flat.append(node)
                total_size += size
    except PasswordRequired as exc:
        raise ArchivePasswordError(_PASSWORD_REQUIRED) from exc
    except Bad7zFile as exc:
        raise ArchivePasswordError(_PASSWORD_INVALID) from exc
    except Py7zrError as exc:
        message = str(exc).lower()
        if "password" in message or "wrong" in message:
            raise ArchivePasswordError(_PASSWORD_INVALID) from exc
        raise

    if encrypted_seen and not password:
        raise ArchivePasswordError(_PASSWORD_REQUIRED)

    nested_tree = nest_flat_entries(flat)
    summary_flags = summarize_flags(flat, max_depth=max((e.path.count("/") for e in flat), default=0), entry_count=entry_count)
    summary = InspectSummary(
        entryCount=entry_count,
        totalUncompressedBytes=total_size,
        totalCompressedBytes=total_size,
        maxDepth=max((e.path.count("/") for e in flat), default=0),
        formatGuess=detect_format(archive_path),
        flags=summary_flags,
        blockedExtract=any(
            flag in summary_flags
            for flag in ("path_traversal", "symlink_escape", "high_compression_ratio")
        ),
        warnings=[],
    )
    return InspectResult(jobId=job_id, filename=filename, tree=nested_tree, summary=summary)
