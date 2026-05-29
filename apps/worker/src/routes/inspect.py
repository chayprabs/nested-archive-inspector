from __future__ import annotations

import uuid
from pathlib import Path

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.core.inspect_dispatch import ArchivePasswordError, inspect_archive_file
from src.core.sandbox import job_workspace
from src.models import ArchiveEntry, InspectResult

router = APIRouter(prefix="/v1", tags=["inspect"])


def _password_error(exc: ArchivePasswordError) -> HTTPException:
    return HTTPException(status_code=401, detail=exc.code)


@router.post("/inspect", response_model=InspectResult)
async def inspect_archive(
    file: UploadFile = File(...),
    password: str | None = Form(default=None),
) -> InspectResult:
    job_id = str(uuid.uuid4())
    suffix = Path(file.filename or "upload.bin").suffix or ".bin"

    with job_workspace() as workspace:
        target = workspace / f"input{suffix}"
        payload = await file.read()
        if not payload:
            raise HTTPException(status_code=400, detail="400_ARCHIVE_EMPTY")
        target.write_bytes(payload)
        try:
            return inspect_archive_file(target, job_id, file.filename or target.name, password)
        except ArchivePasswordError as exc:
            raise _password_error(exc) from exc


@router.post("/inspect/url", response_model=InspectResult)
async def inspect_archive_url(
    url: str = Form(...),
    password: str | None = Form(default=None),
) -> InspectResult:
    from src.core.ingest import fetch_url_archive

    job_id = str(uuid.uuid4())
    try:
        payload, filename = fetch_url_archive(url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=400, detail="400_URL_FETCH_FAILED") from exc

    suffix = Path(filename).suffix or ".bin"
    with job_workspace() as workspace:
        target = workspace / f"input{suffix}"
        target.write_bytes(payload)
        try:
            return inspect_archive_file(target, job_id, filename, password)
        except ArchivePasswordError as exc:
            raise _password_error(exc) from exc


@router.post("/inspect/expand", response_model=list[ArchiveEntry])
async def expand_nested(
    file: UploadFile = File(...),
    entry_path: str = Form(...),
    password: str | None = Form(default=None),
) -> list[ArchiveEntry]:
    from src.core.nested_expand import expand_nested_entry

    job_id = str(uuid.uuid4())
    suffix = Path(file.filename or "upload.bin").suffix or ".bin"

    with job_workspace() as workspace:
        target = workspace / f"input{suffix}"
        target.write_bytes(await file.read())
        try:
            children = expand_nested_entry(target, entry_path, job_id)
        except ArchivePasswordError as exc:
            raise _password_error(exc) from exc
        if not children:
            raise HTTPException(status_code=404, detail="404_NESTED_ENTRY_NOT_FOUND")
        return children
