from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

import httpx

_MAX_URL_BYTES = int(os.getenv("ARCHIVEVET_MAX_URL_BYTES", str(50 * 1024 * 1024)))
_ALLOWED_SCHEMES = {"http", "https"}


def fetch_url_archive(url: str) -> tuple[bytes, str]:
    parsed = urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ValueError("400_URL_SCHEME_NOT_ALLOWED")
    if not parsed.netloc:
        raise ValueError("400_URL_INVALID")

    with httpx.Client(follow_redirects=True, timeout=60.0) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            chunks: list[bytes] = []
            total = 0
            for chunk in response.iter_bytes():
                total += len(chunk)
                if total > _MAX_URL_BYTES:
                    raise ValueError("413_URL_PAYLOAD_TOO_LARGE")
                chunks.append(chunk)
            payload = b"".join(chunks)

    filename = Path(parsed.path).name or "download.bin"
    return payload, filename
