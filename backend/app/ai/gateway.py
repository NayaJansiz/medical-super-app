"""AI gateway: the only way feature code may call an AI model.

Configuration is read from environment variables at call time:
- AI_PROVIDER         provider name (default "mock")
- AI_KILL_SWITCH      "true"/"1"/"yes" blocks every call
- AI_TIMEOUT_SECONDS  per-call timeout in seconds (default 10)

Message content is never logged.
"""

import logging
import os
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError

from app.ai.errors import (
    AIConfigError,
    AIDisabledError,
    AITimeoutError,
    UnknownProviderError,
)
from app.ai.providers.base import Provider
from app.ai.providers.mock import MockProvider
from app.ai.schemas import AIRequest, AIResponse

logger = logging.getLogger("app.ai.gateway")

DEFAULT_PROVIDER = "mock"
DEFAULT_TIMEOUT_SECONDS = 10.0

# Provider registry: name -> factory. Real providers are added here later.
PROVIDERS: dict[str, Callable[[], Provider]] = {
    "mock": MockProvider,
}


def _kill_switch_on() -> bool:
    value = os.environ.get("AI_KILL_SWITCH", "false")
    return value.strip().lower() in {"true", "1", "yes"}


def _timeout_seconds() -> float:
    raw = os.environ.get("AI_TIMEOUT_SECONDS")
    if raw is None or raw.strip() == "":
        return DEFAULT_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError:
        raise AIConfigError(
            f"AI_TIMEOUT_SECONDS must be a number, got {raw!r}"
        ) from None
    if value <= 0:
        raise AIConfigError("AI_TIMEOUT_SECONDS must be greater than 0")
    return value


def _get_provider_name() -> str:
    name = os.environ.get("AI_PROVIDER", DEFAULT_PROVIDER).strip().lower()
    return name or DEFAULT_PROVIDER


def _build_provider(name: str) -> Provider:
    factory = PROVIDERS.get(name)
    if factory is None:
        known = ", ".join(sorted(PROVIDERS))
        raise UnknownProviderError(
            f"Unknown AI provider {name!r}. Known providers: {known}"
        )
    return factory()


def complete(request: AIRequest) -> AIResponse:
    """Route a request to the configured provider, with kill switch and timeout."""
    if _kill_switch_on():
        logger.warning("ai call blocked by kill switch task=%s", request.task)
        raise AIDisabledError("AI is disabled (AI_KILL_SWITCH is on)")

    name = _get_provider_name()
    provider = _build_provider(name)
    timeout = _timeout_seconds()

    start = time.monotonic()
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(provider.complete, request)
    try:
        response = future.result(timeout=timeout)
    except FutureTimeoutError:
        latency_ms = int((time.monotonic() - start) * 1000)
        logger.error(
            "ai call timed out task=%s provider=%s latency_ms=%d",
            request.task,
            name,
            latency_ms,
        )
        raise AITimeoutError(
            f"Provider {name!r} did not answer within {timeout} seconds"
        ) from None
    finally:
        # Do not wait for a stuck provider thread.
        executor.shutdown(wait=False, cancel_futures=True)

    latency_ms = int((time.monotonic() - start) * 1000)
    logger.info(
        "ai call ok task=%s provider=%s latency_ms=%d",
        request.task,
        name,
        latency_ms,
    )
    return response
