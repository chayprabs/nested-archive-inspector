from fastapi.testclient import TestClient

from src.main import app


def test_share_roundtrip():
    client = TestClient(app)
    created = client.post(
        "/v1/share",
        json={"kind": "inspect", "payload": {"jobId": "x", "filename": "a.zip", "tree": [], "summary": {}}},
    )
    assert created.status_code == 200
    token = created.json()["token"]
    fetched = client.get(f"/v1/share/{token}")
    assert fetched.status_code == 200
    assert fetched.json()["payload"]["jobId"] == "x"
