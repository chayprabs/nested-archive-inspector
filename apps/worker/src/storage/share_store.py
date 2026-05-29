from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

ShareKind = Literal["inspect", "diff"]
_TTL_SECONDS = int(os.getenv("ARCHIVEVET_SHARE_TTL_SECONDS", "600"))


@dataclass
class StoredShare:
    kind: ShareKind
    payload: dict[str, Any]
    created_at: datetime
    expires_at: datetime


class ShareStore:
    def __init__(self) -> None:
        self._items: dict[str, StoredShare] = {}

    def create(self, kind: ShareKind, payload: dict[str, Any]) -> tuple[str, StoredShare]:
        now = datetime.now(UTC)
        artifact = StoredShare(
            kind=kind,
            payload=payload,
            created_at=now,
            expires_at=now + timedelta(seconds=_TTL_SECONDS),
        )
        token = secrets.token_urlsafe(12)
        self._items[token] = artifact
        self._purge_expired(now)
        return token, artifact

    def get(self, token: str) -> StoredShare | None:
        now = datetime.now(UTC)
        self._purge_expired(now)
        artifact = self._items.get(token)
        if artifact is None or artifact.expires_at <= now:
            self._items.pop(token, None)
            return None
        return artifact

    def _purge_expired(self, now: datetime) -> None:
        expired = [token for token, artifact in self._items.items() if artifact.expires_at <= now]
        for token in expired:
            self._items.pop(token, None)


share_store = ShareStore()
