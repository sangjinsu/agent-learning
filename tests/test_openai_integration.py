import pytest
from langchain_core.messages import AIMessage, HumanMessage

from agent_learning.llm.chain import ChainService
from agent_learning.llm.chat import ChatService
from agent_learning.llm.graph import GraphInput, GraphService
from agent_learning.llm.observability import run_observable_chat_chain
from agent_learning.llm.openai import integration_enabled, load_config_from_env, new_chat_model
from agent_learning.llm.rag import Document, InMemoryKeywordRetriever, RAGService
from agent_learning.llm.streaming import StreamingService
from agent_learning.llm.toolcalling import ToolCallingService
from agent_learning.tools.calculator import calculator_tool


pytestmark = pytest.mark.skipif(
    not integration_enabled(),
    reason="set RUN_AGENT_LEARNING_INTEGRATION=1 in the environment or .env to call external APIs",
)


def test_openai_chat_model_integration():
    assert integration_enabled() is True
    model = _integration_model("OpenAI chat model")
    answer = ChatService(model).ask("Reply with one short sentence about LangChain.")
    assert answer.strip()


def test_openai_tool_calling_integration():
    model = _integration_model("OpenAI tool calling")

    result = ToolCallingService(model).ask(
        'Use the calculator tool to calculate "12 * (7 + 3)", then answer in one short sentence.',
        [calculator_tool()],
    )

    assert getattr(result.first_response, "tool_calls", [])
    assert result.tool_messages
    assert result.answer.strip()


def test_openai_chain_integration():
    model = _integration_model("OpenAI chain")

    answer = ChainService(model).ask_with_history(
        "In one short sentence, what does LangChain runnable composition do?",
        [
            HumanMessage(content="What did the previous chapter cover?"),
            AIMessage(content="It covered model-backed tool calling."),
        ],
    )

    assert answer.strip()


def test_openai_graph_integration():
    model = _integration_model("OpenAI graph")
    service = GraphService(model)

    calculation = service.run(GraphInput(question="calculate: 12 * (7 + 3)"))
    chat = service.run(
        GraphInput(
            question="In one short sentence, how is LangGraph different from a linear chain?",
            history=[
                HumanMessage(content="What did Chapter 5 cover?"),
                AIMessage(content="It covered Chain."),
            ],
        )
    )

    assert calculation.route == "calculator"
    assert calculation.answer == "12 * (7 + 3) = 120"
    assert chat.route == "chat"
    assert chat.answer.strip()
    assert chat.prompt_messages


def test_openai_streaming_integration():
    model = _integration_model("OpenAI streaming")

    result = StreamingService(model).ask_with_history(
        "In one short sentence, what does streaming provide?",
        [
            HumanMessage(content="What did Chapter 6 cover?"),
            AIMessage(content="It covered graph branching."),
        ],
    )

    assert result.answer.strip()
    assert result.chunks
    assert result.prompt_messages


def test_openai_observability_integration():
    model = _integration_model("OpenAI observability")

    result = run_observable_chat_chain(
        model=model,
        question="한 문장으로 callback observability는 무엇을 관찰하나요?",
        history=[
            HumanMessage(content="Chapter 7에서는 무엇을 다뤘나요?"),
            AIMessage(content="Streaming을 다뤘습니다."),
        ],
    )

    assert result.answer.strip()
    assert result.events
    assert any(event.timing == "start" and event.component == "ChatPromptTemplate" for event in result.events)
    assert any(event.timing == "end" and event.name == "model" for event in result.events)


def test_openai_rag_integration():
    model = _integration_model("OpenAI RAG")
    service = RAGService(
        InMemoryKeywordRetriever(
            [
                Document(
                    id="rag",
                    content=(
                        "Chapter 09 explains retrieval augmented generation with an "
                        "in-memory keyword retriever and source metadata."
                    ),
                    metadata={"title": "Chapter 09 RAG Basics", "source": "integration-fixture"},
                )
            ]
        ),
        model,
    )

    result = service.ask("한 문장으로 Chapter 09 RAG는 무엇을 설명하나요?")

    assert result.answer.strip()
    assert [source.id for source in result.sources] == ["rag"]
    assert result.prompt_messages


def _integration_model(label: str):
    cfg = load_config_from_env()
    if not cfg.api_key.strip():
        pytest.skip(f"set OPENAI_API_KEY to run {label} integration test")
    return new_chat_model(cfg)
