
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SupportedLanguage = Literal["en", "sw"]


class ChatRequest(BaseModel):
    """Validate incoming chatbot messages."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's message, up to 2000 characters.",
    )
    language: SupportedLanguage = Field(
        ...,
        description="Response language: en for English or sw for Kiswahili.",
    )

    @field_validator("message")
    @classmethod
    def validate_message_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message must not be empty or whitespace only.")
        return value


class ChatResponse(BaseModel):
    """Define the standard chatbot response structure."""

    answer: str
    language: SupportedLanguage
    sources: list[dict[str, str]] = Field(default_factory=list)
    safety_notice: str
