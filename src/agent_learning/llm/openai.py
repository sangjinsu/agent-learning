from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values
from langchain_openai import ChatOpenAI

DEFAULT_MODEL = "gpt-4.1-mini"


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str = ""
    model: str = DEFAULT_MODEL
    base_url: str = ""

    def validate(self) -> None:
        if not self.api_key.strip():
            raise ValueError("openai config: OPENAI_API_KEY is required")
        if not self.model.strip():
            raise ValueError("openai config: OPENAI_MODEL must not be blank")


def load_config_from_env() -> OpenAIConfig:
    dotenv = _load_dotenv()
    return OpenAIConfig(
        api_key=_env_value("OPENAI_API_KEY", dotenv),
        model=_env_value("OPENAI_MODEL", dotenv) or DEFAULT_MODEL,
        base_url=_env_value("OPENAI_BASE_URL", dotenv),
    )


def integration_enabled() -> bool:
    return _env_value("RUN_AGENT_LEARNING_INTEGRATION", _load_dotenv()) == "1"


def new_chat_model(config: OpenAIConfig) -> ChatOpenAI:
    config.validate()
    kwargs = {"api_key": config.api_key, "model": config.model}
    if config.base_url:
        kwargs["base_url"] = config.base_url
    return ChatOpenAI(**kwargs)


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
