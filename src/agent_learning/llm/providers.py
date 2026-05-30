from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import dotenv_values

from agent_learning.llm.openai import OpenAIConfig, load_config_from_env, new_chat_model

ProviderName = Literal["openai", "anthropic"]

DEFAULT_PROVIDER: ProviderName = "openai"
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"


@dataclass(frozen=True)
class AnthropicConfig:
    api_key: str = ""
    model: str = DEFAULT_ANTHROPIC_MODEL

    def validate(self) -> None:
        if not self.api_key.strip():
            raise ValueError("anthropic config: ANTHROPIC_API_KEY is required")
        if not self.model.strip():
            raise ValueError("anthropic config: ANTHROPIC_MODEL must not be blank")


@dataclass(frozen=True)
class ModelProviderConfig:
    provider: ProviderName
    openai: OpenAIConfig
    anthropic: AnthropicConfig

    @property
    def active_api_key(self) -> str:
        return self.openai.api_key if self.provider == "openai" else self.anthropic.api_key

    @property
    def active_model(self) -> str:
        return self.openai.model if self.provider == "openai" else self.anthropic.model

    @property
    def active_api_key_name(self) -> str:
        return "OPENAI_API_KEY" if self.provider == "openai" else "ANTHROPIC_API_KEY"


def load_provider_config_from_env() -> ModelProviderConfig:
    dotenv = _load_dotenv()
    provider = (_env_value("AGENT_LEARNING_PROVIDER", dotenv) or DEFAULT_PROVIDER).lower()
    if provider not in ("openai", "anthropic"):
        raise ValueError(f"unsupported provider: {provider}")
    return ModelProviderConfig(
        provider=provider,
        openai=load_config_from_env(),
        anthropic=AnthropicConfig(
            api_key=_env_value("ANTHROPIC_API_KEY", dotenv),
            model=_env_value("ANTHROPIC_MODEL", dotenv) or DEFAULT_ANTHROPIC_MODEL,
        ),
    )


def new_provider_chat_model(config: ModelProviderConfig):
    if config.provider == "openai":
        return new_chat_model(config.openai)

    config.anthropic.validate()
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(
        api_key=config.anthropic.api_key,
        model=config.anthropic.model,
    )


def _env_value(key: str, dotenv: dict[str, str | None]) -> str:
    if key in os.environ:
        return os.environ[key].strip()
    value = dotenv.get(key) or ""
    return value.strip()


def _load_dotenv() -> dict[str, str | None]:
    path = _find_dotenv()
    return dict(dotenv_values(path)) if path else {}


def _find_dotenv() -> Path | None:
    current = Path.cwd()
    for directory in (current, *current.parents):
        candidate = directory / ".env"
        if candidate.exists():
            return candidate
        if (directory / "pyproject.toml").exists():
            return None
    return None
