import importlib.util
import sys
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from agent_learning.fake import FakeChatModel, FakeStreamingChatModel
from agent_learning.llm.chain import ChainService
from agent_learning.llm.chat import ChatService
from agent_learning.llm.graph import GraphInput, GraphService
from agent_learning.llm.observability import run_observable_chat_chain
from agent_learning.llm.openai import OpenAIConfig, integration_enabled, load_config_from_env
from agent_learning.llm.prompting import DEFAULT_SYSTEM_PROMPT, format_messages
from agent_learning.llm.rag import Document, InMemoryKeywordRetriever, RAGService, load_documents
from agent_learning.llm.streaming import StreamingService
from agent_learning.llm.toolcalling import ToolCallingService
from agent_learning.tools.calculator import calculate, calculator_tool


def test_ch01_chat_service_uses_fake_model():
    model = FakeChatModel("fake answer")
    service = ChatService(model)

    assert service.ask("What is LangChain?") == "fake answer"
    assert isinstance(model.last_input[0], SystemMessage)
    assert isinstance(model.last_input[-1], HumanMessage)
    assert model.last_input[-1].content == "What is LangChain?"


def test_ch02_prompt_formats_system_history_and_question():
    history = [HumanMessage(content="hello"), AIMessage(content="hi")]

    messages = format_messages("next?", history)

    assert messages[0].content == DEFAULT_SYSTEM_PROMPT
    assert [message.content for message in messages[1:]] == ["hello", "hi", "next?"]


def test_ch03_config_prefers_environment_and_disables_integration_by_default(monkeypatch):
    monkeypatch.delenv("RUN_AGENT_LEARNING_INTEGRATION", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    monkeypatch.setenv("OPENAI_MODEL", "env-model")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.invalid/v1")

    assert load_config_from_env() == OpenAIConfig(
        api_key="env-key",
        model="env-model",
        base_url="https://example.invalid/v1",
    )
    assert integration_enabled() is False


def test_ch03_example_is_opt_in_and_safe_without_api_key(monkeypatch, capsys):
    example = _load_example("ch03_openai_chatmodel.py")
    monkeypatch.delenv("RUN_AGENT_LEARNING_INTEGRATION", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(sys, "argv", ["ch03_openai_chatmodel.py", "What does ChatOpenAI do?"])

    example.main()

    output = capsys.readouterr().out
    assert "OpenAI integration is disabled." in output
    assert "RUN_AGENT_LEARNING_INTEGRATION=1" in output


def test_ch04_calculator_supports_safe_arithmetic_and_rejects_calls():
    assert calculate("12 * (7 + 3)").result == 120
    assert calculate("-4 + 10 / 2").result == 1
    assert "description" in calculator_tool().args["expression"]

    with pytest.raises(ValueError, match="unsupported expression"):
        calculate("__import__('os').system('rm -rf /')")
    with pytest.raises(ValueError, match="unsupported expression"):
        calculate("True")
    with pytest.raises(ValueError, match="division by zero"):
        calculate("10 / 0")


def test_ch04_tool_calling_executes_calculator_loop():
    service = ToolCallingService(FakeChatModel("unused"))

    result = service.ask("12 * (7 + 3)", [calculator_tool()])

    assert result.answer == "12 * (7 + 3) = 120"
    assert result.tool_messages
    assert isinstance(result.tool_messages[0], ToolMessage)


def test_ch05_chain_service_runs_prompt_model_chain_with_trace():
    model = FakeChatModel("chain answer")
    service = ChainService(model)

    answer = service.ask("How does Chain work?")
    trace = service.ask_with_trace("How does Chain work?")

    assert answer == "chain answer"
    assert trace.answer == "chain answer"
    assert trace.prompt_messages[-1].content == "How does Chain work?"


def test_ch06_graph_routes_calculation_without_model_call_and_chat_with_model_call():
    model = FakeChatModel("graph answer")
    service = GraphService(model)

    calc = service.run(GraphInput(question="calculate: 7 * (8 + 2)"))
    chat = service.run(GraphInput(question="What is LangGraph?"))

    assert calc.route == "calculator"
    assert calc.answer == "7 * (8 + 2) = 70"
    assert model.generate_calls == 1
    assert chat.route == "chat"
    assert chat.answer == "graph answer"


def test_ch07_streaming_collects_chunks():
    service = StreamingService(FakeStreamingChatModel("stream", " ", "answer"))

    result = service.ask("How does streaming work?")

    assert result.answer == "stream answer"
    assert result.chunks == ["stream", " ", "answer"]


def test_ch08_observability_records_chain_events():
    result = run_observable_chat_chain(
        model=FakeChatModel("observable answer"),
        question="How do callbacks help?",
    )

    assert result.answer == "observable answer"
    assert [event.name for event in result.events] == [
        "chain",
        "prompt",
        "prompt",
        "model",
        "model",
        "chain",
    ]
    assert result.events[0].timing == "start"
    assert result.events[-1].timing == "end"


def test_ch09_rag_retrieves_keyword_context_and_sources():
    docs = [
        Document(id="graph", content="LangGraph routes calculator and chat branches.", metadata={"title": "Graph", "source": "graph.md"}),
        Document(id="rag", content="RAG retrieves context and cites sources.", metadata={"title": "RAG", "source": "rag.txt"}),
    ]
    service = RAGService(InMemoryKeywordRetriever(docs), FakeChatModel("grounded answer"))

    result = service.ask("How does RAG retrieve sources?")

    assert result.answer == "grounded answer"
    assert [source.title for source in result.sources] == ["RAG"]
    assert "Retrieved context:" in result.prompt_messages[-1].content


def test_ch09_load_documents_uses_first_text_line_as_title():
    docs = load_documents(Path("testdata/docs/ch09-rag"))
    by_id = {doc.id: doc for doc in docs}

    assert by_id["chapter09-rag-basics"].metadata["title"] == "Chapter 09 RAG Basics"
    assert by_id["chapter06-graph"].metadata["title"] == "Chapter 06 Graph"


def test_integration_flag_example_is_opt_in():
    if not integration_enabled():
        pytest.skip("set RUN_AGENT_LEARNING_INTEGRATION=1 in the environment or .env to call external APIs")
    assert integration_enabled() is True


def _load_example(filename: str):
    path = Path(__file__).resolve().parents[1] / "examples" / filename
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load example: {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
