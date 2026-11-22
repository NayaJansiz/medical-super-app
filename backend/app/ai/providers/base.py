"""The interface every AI provider must implement."""

from typing import Protocol

from app.ai.schemas import AIRequest, AIResponse


class Provider(Protocol):
    def complete(self, request: AIRequest) -> AIResponse: ...
