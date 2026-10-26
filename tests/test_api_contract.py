
from fastapi.testclient import TestClient

from app.core.config import APP_DEBUG, APP_ENV
from app.main import app

client = TestClient(app)


def test_development_configuration_is_not_debug_enabled():
    assert APP_ENV == "development"
    assert APP_DEBUG is False


def test_api_metadata_is_correct():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    metadata = response.json()["info"]
    assert metadata["title"] == "HIV_SRH_Education_Chatbot"
    assert metadata["version"] == "0.1.0"


def test_expected_api_routes_are_registered():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]

    assert "/" in paths
    assert "get" in paths["/"]

    assert "/health" in paths
    assert "get" in paths["/health"]

    assert "/api/v1/languages" in paths
    assert "get" in paths["/api/v1/languages"]

    assert "/api/v1/chat" in paths
    assert "post" in paths["/api/v1/chat"]


def test_health_endpoint_returns_success():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_language_endpoint_returns_supported_languages():
    response = client.get("/api/v1/languages")

    assert response.status_code == 200
    assert response.json() == {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "sw", "name": "Kiswahili"},
        ]
    }


def test_chat_openapi_contract_defines_expected_fields():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()

    operation = schema["paths"]["/api/v1/chat"]["post"]
    assert "200" in operation["responses"]
    assert "422" in operation["responses"]

    response_schema = operation["responses"]["200"]["content"][
        "application/json"
    ]["schema"]

    assert response_schema["$ref"].endswith("/ChatResponse")

    chat_schema = schema["components"]["schemas"]["ChatResponse"]
    assert set(chat_schema["properties"]) == {
        "answer",
        "language",
        "sources",
        "safety_notice",
    }
