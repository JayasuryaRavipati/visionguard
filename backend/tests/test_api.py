from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "VisionGuard API is running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "VisionGuard API"


def test_history():
    response = client.get("/api/history")

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)


def test_reject_non_image():
    files = {
        "file": (
            "test.txt",
            b"This is not an image.",
            "text/plain",
        )
    }

    response = client.post(
        "/api/analyze",
        files=files,
    )

    assert response.status_code == 415


def test_reject_empty_image():
    files = {
        "file": (
            "empty.jpg",
            b"",
            "image/jpeg",
        )
    }

    response = client.post(
        "/api/analyze",
        files=files,
    )

    assert response.status_code == 400