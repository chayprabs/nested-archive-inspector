from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes.diff import router as diff_router
from src.routes.extract import router as extract_router
from src.routes.health import router as health_router
from src.routes.inspect import router as inspect_router
from src.routes.repack import router as repack_router


def _load_cors_origins() -> list[str]:
    configured = os.getenv("ARCHIVEVET_CORS_ORIGINS")
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]


app = FastAPI(title="ArchiveVet Worker", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_load_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(inspect_router)
app.include_router(extract_router)
app.include_router(diff_router)
app.include_router(repack_router)
