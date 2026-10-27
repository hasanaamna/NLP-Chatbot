
from fastapi.testclient import TestClient

from backend.main import app


def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to the NLP Chatbot API"


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_with_greeting():
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={"message": "hello"},
        )

    assert response.status_code == 200

    data = response.json()
    assert data["intent"] == "greeting"
    assert data["method"] == "exact_match"
    assert data["response"]
    assert data["confidence"] == 1.0


def test_chat_with_unknown_message():
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={"message": "tell me about quantum physics"},
        )

    assert response.status_code == 200

    data = response.json()
    assert data["response"]
    assert data["intent"]
    assert 0.0 <= data["confidence"] <= 1.0


def test_chat_with_empty_message():
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={"message": ""},
        )

    assert response.status_code == 422


def test_chat_without_message():
    with TestClient(app) as client:
        response = client.post("/chat", json={})

    assert response.status_code == 422


def test_chat_message_too_long():
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={"message": "a" * 2001},
        )

    assert response.status_code == 422
