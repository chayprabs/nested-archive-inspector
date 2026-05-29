from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.storage.share_store import ShareKind, share_store

router = APIRouter(prefix="/v1", tags=["share"])


class ShareCreateRequest(BaseModel):
    kind: ShareKind
    payload: dict[str, Any] = Field(default_factory=dict)


class ShareCreateResponse(BaseModel):
    token: str
    kind: ShareKind
    expiresAt: str
    sharePath: str


class ShareFetchResponse(BaseModel):
    token: str
    kind: ShareKind
    payload: dict[str, Any]
    expiresAt: str


@router.post("/share", response_model=ShareCreateResponse)
def create_share(request: ShareCreateRequest) -> ShareCreateResponse:
    token, artifact = share_store.create(request.kind, request.payload)
    return ShareCreateResponse(
        token=token,
        kind=request.kind,
        expiresAt=artifact.expires_at.isoformat(),
        sharePath=f"/s/{token}",
    )


@router.get("/share/{token}", response_model=ShareFetchResponse)
def fetch_share(token: str) -> ShareFetchResponse:
    artifact = share_store.get(token)
    if artifact is None:
        raise HTTPException(status_code=404, detail="404_SHARE_NOT_FOUND")
    return ShareFetchResponse(
        token=token,
        kind=artifact.kind,
        payload=artifact.payload,
        expiresAt=artifact.expires_at.isoformat(),
    )
