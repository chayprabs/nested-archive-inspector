from __future__ import annotations

import os
import shutil
import tempfile
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

_JOBS_ROOT = Path(os.getenv("ARCHIVEVET_JOBS_DIR", tempfile.gettempdir())) / "archive-vet-jobs"


def new_job_dir() -> Path:
    job_id = str(uuid.uuid4())
    path = _JOBS_ROOT / job_id
    path.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def job_workspace() -> Iterator[Path]:
    workspace = new_job_dir()
    try:
        yield workspace
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def normalize_extract_path(path: str) -> str:
    cleaned = path.replace("\\", "/").lstrip("/")
    parts: list[str] = []
    for segment in cleaned.split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            raise ValueError("path traversal rejected")
        parts.append(segment)
    return "/".join(parts)
