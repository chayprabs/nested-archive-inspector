from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

pytest.importorskip("libarchive")

from src.main import app

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST = json.loads((FIXTURES / "acceptance-manifest.json").read_text(encoding="utf-8"))


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_extract_nested_release_returns_twelve_so_files(client: TestClient):
    archive = FIXTURES / "nested-release.tar.gz"
    with archive.open("rb") as handle:
        response = client.post(
            "/v1/extract",
            files={"file": (archive.name, handle, "application/gzip")},
            data={"glob": "**/*.so"},
        )
    assert response.status_code == 200
    payload = zipfile.ZipFile(io.BytesIO(response.content))
    extracted = [name for name in payload.namelist() if name != "MANIFEST.json"]
    assert len(extracted) == MANIFEST["nestedSoExtractCount"] == 12
