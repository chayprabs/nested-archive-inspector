from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from src.core.flags import blocked_extract
from src.core.repack import repack_archive
from src.core.sandbox import job_workspace
from src.core.tree import build_tree_from_path

router = APIRouter(prefix="/v1", tags=["repack"])


@router.post("/repack")
async def repack_selected(
    file: UploadFile = File(...),
    glob: str = Form(default="**/*"),
    output_format: str = Form(default="zip"),
) -> Response:
    if output_format not in {"zip", "tar.gz"}:
        raise HTTPException(status_code=400, detail="400_REPACK_FORMAT_UNSUPPORTED")

    job_id = str(uuid.uuid4())
    suffix = Path(file.filename or "upload.zip").suffix or ".zip"

    with job_workspace() as workspace:
        target = workspace / f"input{suffix}"
        target.write_bytes(await file.read())
        inspection = build_tree_from_path(target, job_id, file.filename or target.name)
        if blocked_extract(inspection.summary.flags):
            raise HTTPException(status_code=403, detail="403_REPACK_BLOCKED_BY_FLAGS")

        payload, manifest = repack_archive(target, job_id, glob, output_format)  # type: ignore[arg-type]
        media = "application/zip" if output_format == "zip" else "application/gzip"
        extension = "zip" if output_format == "zip" else "tar.gz"
        headers = {
            "Content-Disposition": f'attachment; filename="{job_id}-repack.{extension}"',
            "X-ArchiveVet-Manifest": json.dumps(manifest),
        }
        return Response(content=payload, media_type=media, headers=headers)
