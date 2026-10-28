
from fastapi.testclient import TestClient

from backend.main import app


class FakeAssistant:
    def __init__(self):
        self.conversations = {}

    def get_response(self, message, conversation_id=None):
        conversation_id = conversation_id or "test-conversation-123"

        self.conversations.setdefault(conversation_id, [])
        self.conversations[conversation_id].append(message)

        if message == "What is Python?":
            response = "Python is a programming language."
        elif message == "Explain it simply.":
            response = "Python is a language used to give instructions to computers."
        else:
            response = f"AI response to: {message}"

        return {
            "conversation_id": conversation_id,
            "response": response,
            "model": "test-model",
        }


def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to the AI Assistant API"


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_returns_ai_response():
    with TestClient(app) as client:
        app.state.assistant = FakeAssistant()
        response = client.post(
            "/chat",
            json={"message": "What is Python?"},
        )

    assert response.status_code == 200

    data = response.json()
    assert data["response"] == "Python is a programming language."
    assert data["conversation_id"] == "test-conversation-123"
    assert data["method"] == "groq_api"
    assert data["model"] == "test-model"


def test_chat_accepts_existing_conversation_id():
    with TestClient(app) as client:
        app.state.assistant = FakeAssistant()
        response = client.post(
            "/chat",
            json={
                "message": "Explain it simply.",
                "conversation_id": "conversation-456",
            },
        )

    assert response.status_code == 200
    assert response.json()["conversation_id"] == "conversation-456"


def test_chat_with_empty_message():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": ""})

    assert response.status_code == 422


def test_chat_without_message():
    with TestClient(app) as client:
        response = client.post("/chat", json={})

    assert response.status_code == 422


def test_chat_message_too_long():
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={"message": "a" * 8001},
        )

    assert response.status_code == 422


def test_chat_rejects_empty_conversation_id():
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "message": "Hello",
                "conversation_id": "",
            },
        )

    assert response.status_code == 422
