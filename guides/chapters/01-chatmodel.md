# Chapter 01. ChatModel

## 목표

- LangChain chat model의 기본 역할을 이해합니다.
- `FakeChatModel`을 만들어 외부 API 없이 질문/응답 흐름을 테스트합니다.
- 이후 OpenAI 모델로 교체 가능한 service 경계를 만듭니다.

## 핵심 개념

- `src/agent_learning/fake.py`는 테스트용 fake chat model을 제공합니다.
- `src/agent_learning/llm/chat.py`의 `ChatService`는 model을 받아 질문/응답 흐름을 실행합니다.
- `examples/ch01_chatmodel.py`는 fake model을 사용하는 최소 실행 예제입니다.

## 실행 명령

```bash
uv run python examples/ch01_chatmodel.py "What is LangChain?"
```

## 확인할 출력/테스트

CLI에서 확인할 부분:

- `mode: fake`로 외부 API 없이 실행되는지 확인합니다.
- 기본 출력에서 question과 final answer를 확인합니다.
- `--verbose` 출력에서 `prompt messages`에 user question이 들어가는지 확인합니다.
- `final answer`가 fake model의 deterministic answer로 출력되는지 확인합니다.

테스트:

```bash
uv run pytest tests/test_chapters.py::test_ch01_chat_service_uses_fake_model -q
```

## 다음 장

Chapter 02에서는 system/user/assistant message와 prompt template을 구조화합니다.
