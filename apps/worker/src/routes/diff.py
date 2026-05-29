from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, File, UploadFile

from src.core.diff import diff_archives
from src.core.sandbox import job_workspace
from src.models import DiffResult

router = APIRouter(prefix="/v1", tags=["diff"])


@router.post("/diff", response_model=DiffResult)
async def diff_two_archives(
    left: UploadFile = File(...),
    right: UploadFile = File(...),
) -> DiffResult:
    job_id = str(uuid.uuid4())
    with job_workspace() as workspace:
        left_path = workspace / f"left{Path(left.filename or 'a.zip').suffix or '.zip'}"
        right_path = workspace / f"right{Path(right.filename or 'b.zip').suffix or '.zip'}"
        left_path.write_bytes(await left.read())
        right_path.write_bytes(await right.read())
        result = diff_archives(left_path, right_path)
        result.jobId = job_id
        return result
