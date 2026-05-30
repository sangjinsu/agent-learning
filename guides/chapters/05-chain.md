# Chapter 05. Chain 구성

## 목표

- LangChain runnable composition으로 선형 component pipeline을 구성합니다.
- 기존 `ChatPromptTemplate -> ChatModel` 흐름을 직접 호출 대신 `prompt | model` runnable로 실행합니다.
- unit test는 fake model로 검증하고, integration test는 실제 `ChatOpenAI`로 실행합니다.

## 핵심 개념

- Chain은 component를 순서대로 연결해 하나의 runnable처럼 실행합니다.
- 이번 장의 Chain은 `dict[str, object] -> ChatPromptTemplate -> ChatModel -> BaseMessage` 흐름입니다.
- `ChainService.ask_with_trace()`는 input variables, prompt messages, model response를 단계별로 보여줍니다.
- tool calling처럼 반복이나 조건이 필요한 흐름은 이후 Graph/Agent 장에서 더 자연스럽게 다룹니다.

## 실행 명령

```bash
uv run python examples/ch05_chain.py "How does Chain work?"
```

## 확인할 출력/테스트

CLI에서 확인할 부분:

- `chain input`에서 runnable에 전달되는 입력 변수를 확인합니다.
- `prompt messages`에서 prompt template 결과를 확인합니다.
- `final answer`가 `ChatPromptTemplate -> ChatModel` chain 결과로 출력되는지 확인합니다.

테스트:

```bash
uv run pytest tests/test_chapters.py::test_ch05_chain_service_runs_prompt_model_chain_with_trace -q
RUN_AGENT_LEARNING_INTEGRATION=1 uv run pytest tests/test_openai_integration.py::test_openai_chain_integration -v
```
