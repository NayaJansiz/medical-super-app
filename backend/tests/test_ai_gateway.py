import logging
import time

import pytest

from app.ai import gateway
from app.ai.errors import (
    AIConfigError,
    AIDisabledError,
    AITimeoutError,
    UnknownProviderError,
)
from app.ai.schemas import AIRequest, AIResponse, Message

SECRET_TEXT = "patient-secret-text-12345"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ("AI_PROVIDER", "AI_KILL_SWITCH", "AI_TIMEOUT_SECONDS"):
        monkeypatch.delenv(var, raising=False)


def make_request(task: str = "chat", content: str = "hello") -> AIRequest:
    return AIRequest(task=task, messages=[Message(role="user", content=content)])


class SlowProvider:
    def complete(self, request: AIRequest) -> AIResponse:
        time.sleep(1.0)
        return AIResponse(text="too late", provider="slow")


def test_mock_returns_canned_response() -> None:
    response = gateway.complete(make_request("chat"))
    assert response.provider == "mock"
    assert response.text == "This is a mock chat response."
    assert response.cached is False


def test_mock_default_response_for_unknown_task() -> None:
    response = gateway.complete(make_request("something-else"))
    assert response.text == "This is a mock response."


@pytest.mark.parametrize("value", ["true", "TRUE", "1", "yes"])
def test_kill_switch_blocks_calls(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("AI_KILL_SWITCH", value)
    with pytest.raises(AIDisabledError):
        gateway.complete(make_request())


def test_kill_switch_off_allows_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_KILL_SWITCH", "false")
    assert gateway.complete(make_request()).provider == "mock"


def test_unknown_provider_raises_clear_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AI_PROVIDER", "nope")
    with pytest.raises(UnknownProviderError) as exc:
        gateway.complete(make_request())
    assert "nope" in str(exc.value)
    assert "mock" in str(exc.value)


def test_timeout_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(gateway.PROVIDERS, "slow", SlowProvider)
    monkeypatch.setenv("AI_PROVIDER", "slow")
    monkeypatch.setenv("AI_TIMEOUT_SECONDS", "0.1")
    start = time.monotonic()
    with pytest.raises(AITimeoutError):
        gateway.complete(make_request())
    assert time.monotonic() - start < 0.9  # did not wait for the slow provider


@pytest.mark.parametrize("value", ["abc", "0", "-5"])
def test_invalid_timeout_config_raises(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("AI_TIMEOUT_SECONDS", value)
    with pytest.raises(AIConfigError):
        gateway.complete(make_request())


def test_logs_do_not_contain_message_content(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.DEBUG, logger="app.ai.gateway"):
        gateway.complete(make_request(content=SECRET_TEXT))
    assert caplog.records  # something was logged
    assert SECRET_TEXT not in caplog.text
    assert "task=chat" in caplog.text
    assert "provider=mock" in caplog.text


def test_empty_messages_rejected() -> None:
    with pytest.raises(ValueError):
        AIRequest(task="chat", messages=[])
