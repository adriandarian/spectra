"""
LLM Manager - Unified interface for multiple LLM providers.

Provides automatic provider selection, fallback, and common use cases.
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .base import LLMConfig, LLMMessage, LLMProvider, LLMResponse, LLMRole


logger = logging.getLogger(__name__)


class ProviderName(Enum):
    """Supported LLM provider names."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"


@dataclass
class LLMManagerConfig:
    """Configuration for LLM Manager."""

    # Provider preference order
    provider_order: list[ProviderName] = field(
        default_factory=lambda: [
            ProviderName.ANTHROPIC,
            ProviderName.OPENAI,
            ProviderName.GOOGLE,
        ]
    )

    # API keys (optional, will use env vars if not set)
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    google_api_key: str | None = None

    # Default settings
    max_tokens: int = 4096
    temperature: float = 0.7

    # Fallback behavior
    enable_fallback: bool = True


class LLMManager:
    """
    Manages multiple LLM providers with automatic selection and fallback.
    """

    def __init__(self, config: LLMManagerConfig | None = None):
        """
        Initialize the LLM manager.

        Args:
            config: Manager configuration.
        """
        self.config = config or LLMManagerConfig()
        self.providers: dict[ProviderName, LLMProvider] = {}
        self.logger = logging.getLogger("LLMManager")

        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize available providers based on configuration."""
        # Try Anthropic
        anthropic_key = self.config.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        if anthropic_key:
            try:
                from .anthropic import AnthropicProvider

                provider = AnthropicProvider(
                    LLMConfig(
                        api_key=anthropic_key,
                        max_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                    )
                )
                if provider.is_available():
                    self.providers[ProviderName.ANTHROPIC] = provider
                    self.logger.debug("Anthropic provider initialized")
            except ImportError:
                self.logger.debug("Anthropic SDK not installed")

        # Try OpenAI
        openai_key = self.config.openai_api_key or os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                from .openai import OpenAIProvider

                provider = OpenAIProvider(
                    LLMConfig(
                        api_key=openai_key,
                        max_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                    )
                )
                if provider.is_available():
                    self.providers[ProviderName.OPENAI] = provider
                    self.logger.debug("OpenAI provider initialized")
            except ImportError:
                self.logger.debug("OpenAI SDK not installed")

        # Try Google
        google_key = self.config.google_api_key or os.environ.get("GOOGLE_API_KEY")
        if google_key:
            try:
                from .google import GoogleProvider

                provider = GoogleProvider(
                    LLMConfig(
                        api_key=google_key,
                        max_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                    )
                )
                if provider.is_available():
                    self.providers[ProviderName.GOOGLE] = provider
                    self.logger.debug("Google provider initialized")
            except ImportError:
                self.logger.debug("Google SDK not installed")

    @property
    def available_providers(self) -> list[ProviderName]:
        """Get list of available providers."""
        return list(self.providers.keys())

    @property
    def primary_provider(self) -> LLMProvider | None:
        """Get the primary (first available) provider."""
        for name in self.config.provider_order:
            if name in self.providers:
                return self.providers[name]
        return None

    def get_provider(self, name: ProviderName | str) -> LLMProvider | None:
        """Get a specific provider by name."""
        if isinstance(name, str):
            try:
                name = ProviderName(name.lower())
            except ValueError:
                return None
        return self.providers.get(name)

    def is_available(self) -> bool:
        """Check if any provider is available."""
        return len(self.providers) > 0

    def complete(
        self,
        messages: list[LLMMessage],
        provider: ProviderName | str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a completion using the best available provider.

        Args:
            messages: List of messages.
            provider: Optional specific provider to use.
            **kwargs: Additional options.

        Returns:
            LLMResponse with the completion.

        Raises:
            RuntimeError: If no providers are available.
        """
        # Determine which provider to use
        if provider:
            llm = self.get_provider(provider)
            if not llm:
                raise RuntimeError(f"Provider '{provider}' not available")
            return llm.complete(messages, **kwargs)

        # Use primary provider
        llm = self.primary_provider
        if not llm:
            raise RuntimeError(
                "No LLM providers available. Set one of: "
                "ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY"
            )

        # Try with fallback
        if self.config.enable_fallback:
            return self._complete_with_fallback(messages, **kwargs)

        return llm.complete(messages, **kwargs)

    def _complete_with_fallback(
        self,
        messages: list[LLMMessage],
        **kwargs: Any,
    ) -> LLMResponse:
        """Complete with fallback to other providers on failure."""
        errors = []

        for name in self.config.provider_order:
            if name not in self.providers:
                continue

            provider = self.providers[name]
            try:
                return provider.complete(messages, **kwargs)
            except Exception as e:
                self.logger.warning(f"{name.value} failed: {e}")
                errors.append(f"{name.value}: {e}")

        raise RuntimeError(f"All providers failed: {'; '.join(errors)}")

    def prompt(
        self,
        user_message: str,
        system_prompt: str | None = None,
        provider: ProviderName | str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Simple single-turn prompt.

        Args:
            user_message: The user's message.
            system_prompt: Optional system prompt.
            provider: Optional specific provider.
            **kwargs: Additional options.

        Returns:
            LLMResponse with the completion.
        """
        messages = []

        if system_prompt:
            messages.append(LLMMessage(role=LLMRole.SYSTEM, content=system_prompt))

        messages.append(LLMMessage(role=LLMRole.USER, content=user_message))

        return self.complete(messages, provider=provider, **kwargs)

    def get_status(self) -> dict[str, Any]:
        """Get status of all providers."""
        status = {
            "available": self.is_available(),
            "providers": {},
        }

        for name in ProviderName:
            provider = self.providers.get(name)
            if provider:
                status["providers"][name.value] = {
                    "available": True,
                    "models": provider.available_models,
                    "default_model": provider.default_model,
                }
            else:
                status["providers"][name.value] = {"available": False}

        if self.primary_provider:
            status["primary"] = self.primary_provider.name

        return status


def create_llm_manager(
    anthropic_api_key: str | None = None,
    openai_api_key: str | None = None,
    google_api_key: str | None = None,
    prefer_provider: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    enable_fallback: bool = True,
) -> LLMManager:
    """
    Create an LLM manager with the given settings.

    Args:
        anthropic_api_key: Anthropic API key.
        openai_api_key: OpenAI API key.
        google_api_key: Google API key.
        prefer_provider: Preferred provider name (anthropic, openai, google).
        max_tokens: Maximum tokens to generate.
        temperature: Sampling temperature.
        enable_fallback: Enable fallback to other providers on failure.

    Returns:
        Configured LLMManager.
    """
    # Determine provider order
    provider_order = [
        ProviderName.ANTHROPIC,
        ProviderName.OPENAI,
        ProviderName.GOOGLE,
    ]

    if prefer_provider:
        try:
            preferred = ProviderName(prefer_provider.lower())
            provider_order.remove(preferred)
            provider_order.insert(0, preferred)
        except ValueError:
            pass

    config = LLMManagerConfig(
        provider_order=provider_order,
        anthropic_api_key=anthropic_api_key,
        openai_api_key=openai_api_key,
        google_api_key=google_api_key,
        max_tokens=max_tokens,
        temperature=temperature,
        enable_fallback=enable_fallback,
    )

    return LLMManager(config)
