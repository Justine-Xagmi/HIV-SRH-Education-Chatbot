
import pytest
from pydantic import ValidationError

from app.api.schemas import ChatRequest, ChatResponse


def test_valid_english_request():
    request = ChatRequest(
        message="What is HIV?",
        language="en",
    )

    assert request.message == "What is HIV?"
    assert request.language == "en"


def test_valid_kiswahili_request():
    request = ChatRequest(
        message="VVU ni nini?",
        language="sw",
    )

    assert request.language == "sw"


@pytest.mark.parametrize("message", ["", "   ", "\n\t"])
def test_rejects_empty_or_whitespace_message(message):
    with pytest.raises(ValidationError):
        ChatRequest(message=message, language="en")


def test_rejects_message_over_2000_characters():
    with pytest.raises(ValidationError):
        ChatRequest(message="a" * 2001, language="en")


def test_accepts_message_at_2000_characters():
    request = ChatRequest(message="a" * 2000, language="en")

    assert len(request.message) == 2000


@pytest.mark.parametrize("language", ["fr", "swahili", "EN", ""])
def test_rejects_unsupported_language(language):
    with pytest.raises(ValidationError):
        ChatRequest(message="Hello", language=language)


def test_rejects_missing_language():
    with pytest.raises(ValidationError):
        ChatRequest(message="Hello")


def test_rejects_unexpected_request_fields():
    with pytest.raises(ValidationError):
        ChatRequest(
            message="Hello",
            language="en",
            unexpected_field="value",
        )


def test_chat_response_structure():
    response = ChatResponse(
        answer="Example educational response.",
        language="en",
        sources=[],
        safety_notice="Educational information only.",
    )

    assert response.language == "en"
    assert response.sources == []
    assert response.safety_notice == "Educational information only."
