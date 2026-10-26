
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_languages_endpoint_returns_english_and_kiswahili():
    response = client.get("/api/v1/languages")

    assert response.status_code == 200
    assert response.json() == {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "sw", "name": "Kiswahili"},
        ]
    }


def test_existing_root_endpoint_still_works():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


def test_existing_health_endpoint_still_works():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
