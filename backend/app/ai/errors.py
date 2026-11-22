"""Custom errors raised by the AI gateway."""


class AIGatewayError(Exception):
    """Base class for all gateway errors."""


class AIDisabledError(AIGatewayError):
    """The kill switch (AI_KILL_SWITCH) is on; AI calls are blocked."""


class UnknownProviderError(AIGatewayError):
    """AI_PROVIDER names a provider that is not registered."""


class AITimeoutError(AIGatewayError):
    """The provider did not answer within AI_TIMEOUT_SECONDS."""


class AIConfigError(AIGatewayError):
    """A gateway environment variable has an invalid value."""
