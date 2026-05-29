from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

pytest.importorskip("py7zr")
pytest.importorskip("libarchive")

from src.main import app

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_encrypted_7z_requires_password(client: TestClient):
    archive = FIXTURES / "encrypted.7z"
    with archive.open("rb") as handle:
        response = client.post(
            "/v1/inspect",
            files={"file": (archive.name, handle, "application/x-7z-compressed")},
        )
    assert response.status_code == 401
    assert "401_ARCHIVE_PASSWORD" in response.json()["detail"]


def test_encrypted_7z_opens_with_password(client: TestClient):
    archive = FIXTURES / "encrypted.7z"
    with archive.open("rb") as handle:
        response = client.post(
            "/v1/inspect",
            files={"file": (archive.name, handle, "application/x-7z-compressed")},
            data={"password": "demo"},
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["entryCount"] >= 1
