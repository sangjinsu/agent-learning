# Chapter 03. Provider ChatModel 연동

## 목표

- `ChatOpenAI` 또는 `ChatAnthropic`을 `ChatService`에 주입합니다.
- `.env` 또는 환경 변수의 provider/API key/model 설정을 분리합니다.
- 실제 API 호출은 `RUN_AGENT_LEARNING_INTEGRATION=1`일 때만 실행되게 만듭니다.

## 핵심 개념

- `src/agent_learning/llm/openai.py`는 `OpenAIConfig`, `load_config_from_env()`, `new_chat_model()`을 제공합니다.
- `src/agent_learning/llm/providers.py`는 `AGENT_LEARNING_PROVIDER=openai|anthropic` 선택을 처리합니다.
- 기본 모델명은 `.env.example`과 같은 `gpt-4.1-mini`입니다.
- unit test는 API를 호출하지 않고, integration test만 opt-in으로 실제 provider API를 호출합니다.
- `examples/ch03_openai_chatmodel.py`는 integration flag가 없으면 API 호출 없이 fake fallback trace를 출력합니다.

## 실행 명령

```bash
uv run python examples/ch03_openai_chatmodel.py "What does ChatOpenAI do?"
RUN_AGENT_LEARNING_INTEGRATION=1 uv run python examples/ch03_openai_chatmodel.py "What does ChatOpenAI do?"
RUN_AGENT_LEARNING_INTEGRATION=1 AGENT_LEARNING_PROVIDER=anthropic uv run python examples/ch03_openai_chatmodel.py "What does ChatAnthropic do?"
```

## 확인할 출력/테스트

CLI에서 확인할 부분:

- integration flag가 없으면 fake fallback으로 실행되어 실제 API를 호출하지 않는지 확인합니다.
- `prompt messages`와 `final answer`가 Chapter 01-02와 같은 service 경계에서 출력되는지 확인합니다.
- `RUN_AGENT_LEARNING_INTEGRATION=1`일 때만 실제 provider 호출 경로를 확인합니다.

테스트:

```bash
uv run pytest tests/test_chapters.py::test_ch03_example_is_opt_in_and_safe_without_api_key -q
uv run pytest tests/test_chapters.py::test_ch03_provider_config_supports_anthropic -q
RUN_AGENT_LEARNING_INTEGRATION=1 uv run pytest tests/test_openai_integration.py::test_openai_chat_model_integration -v
```
