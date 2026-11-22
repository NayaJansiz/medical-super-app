"""Request and response models for the AI gateway."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class AIRequest(BaseModel):
    task: str = Field(min_length=1)
    messages: list[Message] = Field(min_length=1)
    response_schema: dict[str, Any] | None = None


class AIResponse(BaseModel):
    text: str
    provider: str
    cached: bool = False
