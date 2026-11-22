"""Mock provider: canned answers, no network, no quota."""

from app.ai.schemas import AIRequest, AIResponse

CANNED_RESPONSES: dict[str, str] = {
    "chat": "This is a mock chat response.",
    "summarize": "This is a mock summary.",
}
DEFAULT_RESPONSE = "This is a mock response."


class MockProvider:
    name = "mock"

    def complete(self, request: AIRequest) -> AIResponse:
        text = CANNED_RESPONSES.get(request.task, DEFAULT_RESPONSE)
        return AIResponse(text=text, provider=self.name)
