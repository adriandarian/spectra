"""
LLM Adapters - Native integrations with AI providers.

This module provides direct API integrations with:
- Anthropic (Claude)
- OpenAI (GPT-4, GPT-3.5)
- Google (Gemini)
"""

from .base import (
    LLMConfig,
    LLMMessage,
    LLMProvider,
    LLMResponse,
    LLMRole,
    MessageContent,
)
from .manager import (
    LLMManager,
    create_llm_manager,
)


__all__ = [
    "LLMConfig",
    "LLMManager",
    "LLMMessage",
    "LLMProvider",
    "LLMResponse",
    "LLMRole",
    "MessageContent",
    "create_llm_manager",
]

# Optional imports for specific providers
try:
    from .anthropic import AnthropicProvider

    __all__.append("AnthropicProvider")
except ImportError:
    pass

try:
    from .openai import OpenAIProvider

    __all__.append("OpenAIProvider")
except ImportError:
    pass

try:
    from .google import GoogleProvider

    __all__.append("GoogleProvider")
except ImportError:
    pass
