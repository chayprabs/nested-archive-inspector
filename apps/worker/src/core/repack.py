from __future__ import annotations

import io
import json
import tarfile
import zipfile
from pathlib import Path
from typing import Literal

import libarchive

from src.core.glob_match import glob_match
from src.core.sandbox import normalize_extract_path

RepackFormat = Literal["zip", "tar.gz"]


def repack_archive(
    archive_path: Path,
    job_id: str,
    glob: str,
    output_format: RepackFormat,
) -> tuple[bytes, dict[str, object]]:
    entries: list[dict[str, object]] = []
    buffer = io.BytesIO()

    if output_format == "zip":
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as output:
            with libarchive.file_reader(str(archive_path)) as archive:
                for entry in archive:
                    pathname = entry.pathname or ""
                    if entry.isdir or not glob_match(glob, pathname):
                        continue
                    safe_path = normalize_extract_path(pathname)
                    payload = b"".join(entry.get_blocks())
                    output.writestr(safe_path, payload)
                    entries.append({"path": safe_path, "size": len(payload)})
    else:
        with tarfile.open(fileobj=buffer, mode="w:gz") as output:
            with libarchive.file_reader(str(archive_path)) as archive:
                for entry in archive:
                    pathname = entry.pathname or ""
                    if entry.isdir or not glob_match(glob, pathname):
                        continue
                    safe_path = normalize_extract_path(pathname)
                    payload = b"".join(entry.get_blocks())
                    info = tarfile.TarInfo(name=safe_path)
                    info.size = len(payload)
                    output.addfile(info, io.BytesIO(payload))
                    entries.append({"path": safe_path, "size": len(payload)})

    manifest = {
        "jobId": job_id,
        "format": output_format,
        "glob": glob,
        "entries": entries,
        "normalized": {"timestamps": "unchanged", "permissions": "unchanged"},
    }
    buffer.seek(0)
    return buffer.read(), manifest
