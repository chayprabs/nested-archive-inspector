from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.core.sandbox import job_workspace
from src.core.tree import build_tree_from_path
from src.models import InspectResult

router = APIRouter(prefix="/v1", tags=["inspect"])


@router.post("/inspect", response_model=InspectResult)
async def inspect_archive(
    file: UploadFile = File(...),
    password: str | None = Form(default=None),
) -> InspectResult:
    if password:
        raise HTTPException(status_code=501, detail="501_ARCHIVE_PASSWORD_NOT_IMPLEMENTED")

    job_id = str(uuid.uuid4())
    suffix = Path(file.filename or "upload.bin").suffix or ".bin"

    with job_workspace() as workspace:
        target = workspace / f"input{suffix}"
        payload = await file.read()
        if not payload:
            raise HTTPException(status_code=400, detail="400_ARCHIVE_EMPTY")
        target.write_bytes(payload)
        return build_tree_from_path(target, job_id, file.filename or target.name)
