from __future__ import annotations

import io
import json
import uuid
import zipfile
from pathlib import Path

import libarchive
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from src.core.flags import blocked_extract
from src.core.glob_match import glob_match
from src.core.sandbox import job_workspace, normalize_extract_path
from src.core.inspect_dispatch import inspect_archive_file
from src.models import InspectResult

router = APIRouter(prefix="/v1", tags=["extract"])


@router.post("/extract")
async def extract_selected(
    file: UploadFile = File(...),
    glob: str = Form(default="**/*"),
) -> StreamingResponse:
    job_id = str(uuid.uuid4())
    suffix = Path(file.filename or "upload.zip").suffix or ".zip"

    with job_workspace() as workspace:
        target = workspace / f"input{suffix}"
        payload = await file.read()
        target.write_bytes(payload)
        inspection: InspectResult = inspect_archive_file(target, job_id, file.filename or target.name)
        if blocked_extract(inspection.summary.flags):
            raise HTTPException(status_code=403, detail="403_EXTRACT_BLOCKED_BY_FLAGS")

        buffer = io.BytesIO()
        manifest: list[dict[str, object]] = []
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as output:
            with libarchive.file_reader(str(target)) as archive:
                for entry in archive:
                    pathname = entry.pathname or ""
                    if entry.isdir:
                        continue
                    if not glob_match(glob, pathname):
                        continue
                    safe_path = normalize_extract_path(pathname)
                    payload_bytes = b"".join(entry.get_blocks())
                    output.writestr(safe_path, payload_bytes)
                    manifest.append({"path": safe_path, "size": len(payload_bytes)})

            output.writestr(
                "MANIFEST.json",
                json.dumps({"jobId": job_id, "entries": manifest}, indent=2),
            )

        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{job_id}-extract.zip"'},
        )
