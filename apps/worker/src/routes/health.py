from __future__ import annotations

import os

from fastapi import APIRouter

from src.core.formats import SUPPORTED_READ_FORMATS

router = APIRouter(tags=["health"])


@router.get("/health")
@router.get("/v1/health")
def healthcheck() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "archive-vet-worker",
        "formats": list(SUPPORTED_READ_FORMATS),
        "limits": {
            "maxArchiveDepth": int(os.getenv("MAX_ARCHIVE_DEPTH", "8")),
            "maxEntries": int(os.getenv("MAX_ENTRIES", "200000")),
            "maxExtractBytes": int(os.getenv("MAX_EXTRACT_BYTES", str(5 * 1024**3))),
        },
    }
