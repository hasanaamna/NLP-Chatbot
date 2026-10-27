
import pytest

from src.nlp.chatbot import NLPChatbot


@pytest.fixture(scope="module")
def chatbot():
    return NLPChatbot()


@pytest.mark.parametrize(
    "message, expected_intent",
    [
        ("hello", "greeting"),
        ("hi there", "greeting"),
        ("who are you", "bot_identity"),
        ("what can you do", "help"),
        ("thank you", "thanks"),
        ("goodbye", "goodbye"),
        ("what is NLP", "capabilities"),
    ],
)
def test_known_messages(chatbot, message, expected_intent):
    result = chatbot.get_response(message)

    assert result["intent"] == expected_intent
    assert result["response"]
    assert result["method"] == "exact_match"


def test_empty_message(chatbot):
    result = chatbot.get_response("")

    assert result["intent"] == "fallback"
    assert result["confidence"] == 0.0
    assert result["response"]


def test_whitespace_message(chatbot):
    result = chatbot.get_response("   ")

    assert result["intent"] == "fallback"
    assert result["response"]


def test_case_insensitive_matching(chatbot):
    result = chatbot.get_response("HELLO")

    assert result["intent"] == "greeting"
    assert result["method"] == "exact_match"


def test_repeated_spaces(chatbot):
    result = chatbot.get_response("  hello   ")

    assert result["intent"] == "greeting"
    assert result["method"] == "exact_match"


def test_unknown_message_returns_valid_result(chatbot):
    result = chatbot.get_response("tell me about quantum physics")

    assert result["intent"] in chatbot.intents
    assert result["response"]
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["method"] in {
        "exact_match",
        "model_prediction",
        "low_confidence",
        "input_validation",
    }
