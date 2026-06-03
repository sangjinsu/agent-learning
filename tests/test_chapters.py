import importlib.util
import sys
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from agent_learning.example_support import ExampleModelSelection
from agent_learning.fake import FakeChatModel, FakeStreamingChatModel
from agent_learning.llm.chain import ChainService
from agent_learning.llm.chat import ChatService
from agent_learning.llm.graph import GraphInput, GraphService
from agent_learning.llm.observability import run_observable_chat_chain
from agent_learning.llm.openai import OpenAIConfig, integration_enabled, load_config_from_env
from agent_learning.llm.providers import AnthropicConfig, ModelProviderConfig, load_provider_config_from_env
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
    monkeypatch.setenv("RUN_AGENT_LEARNING_INTEGRATION", "0")
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
    monkeypatch.setenv("RUN_AGENT_LEARNING_INTEGRATION", "0")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setattr(sys, "argv", ["ch03_openai_chatmodel.py", "What does ChatOpenAI do?"])

    example.main()

    output = capsys.readouterr().out
    assert "mode: fake" in output
    assert "note: external API disabled; using fake fallback." in output
    assert "final answer: Fake OpenAI-style answer from chapter 03." in output


def test_ch03_provider_config_supports_anthropic(monkeypatch):
    monkeypatch.setenv("AGENT_LEARNING_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-test")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("OPENAI_MODEL", "openai-test")

    config = load_provider_config_from_env()

    assert config.provider == "anthropic"
    assert config.anthropic == AnthropicConfig(api_key="anthropic-key", model="claude-test")
    assert config.openai == OpenAIConfig(api_key="openai-key", model="openai-test", base_url="")
    assert config.active_api_key == "anthropic-key"
    assert config.active_model == "claude-test"


def test_ch03_provider_config_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("AGENT_LEARNING_PROVIDER", "unknown")

    with pytest.raises(ValueError, match="unsupported provider"):
        load_provider_config_from_env()


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
    assert by_id["chapter04-tool-calling"].metadata["title"] == "Chapter 04 Tool Calling"
    assert by_id["chapter07-streaming"].metadata["title"] == "Chapter 07 Streaming"


def test_ch09_korean_callback_question_prioritizes_callback_and_rag_docs():
    docs = load_documents(Path("testdata/docs/ch09-rag"))
    retriever = InMemoryKeywordRetriever(docs)

    retrieved = retriever.retrieve("Chapter 8 callback은 RAG에서 어떤 흐름을 관찰하나요?")

    assert [doc.id for doc in retrieved] == [
        "chapter08-callback-observability",
        "chapter09-rag-basics",
    ]


def test_ch09_extra_rag_examples_cover_tool_calling_and_streaming():
    docs = load_documents(Path("testdata/docs/ch09-rag"))
    retriever = InMemoryKeywordRetriever(docs)

    cases = [
        (
            "tool calling calculator schema safe arithmetic",
            "chapter04-tool-calling",
        ),
        (
            "streaming chunk final answer user interface",
            "chapter07-streaming",
        ),
    ]

    for question, expected_id in cases:
        retrieved = retriever.retrieve(question)
        assert retrieved, question
        assert retrieved[0].id == expected_id


def test_ch10_mcp_demo_exposes_tool_resource_and_prompt_over_stdio():
    import asyncio

    from agent_learning.mcp_demo import run_mcp_demo

    result = asyncio.run(run_mcp_demo("mcp"))

    assert result.flow == "full"
    assert "client -> initialize" in result.trace
    assert "client -> list_tools" in result.trace
    assert any(step.startswith("client -> read_resource uri=chapter://mcp") for step in result.trace)
    assert any(step.startswith("client -> get_prompt name=review_chapter") for step in result.trace)
    assert any(step.startswith("client -> call_tool name=summarize_chapter") for step in result.trace)
    assert "summarize_chapter" in result.tool_names
    assert "chapter://{chapter}" in result.resource_templates
    assert "review_chapter" in result.prompt_names
    assert "Model Context Protocol" in result.resource_content
    assert "Review Chapter 10 MCP" in result.prompt_text
    assert "MCP connects hosts to external capabilities" in result.tool_result
    assert result.final_answer == "MCP stdio full demo completed."


def test_ch10_mcp_demo_supports_focused_flows():
    import asyncio

    from agent_learning.mcp_demo import run_mcp_demo

    discover = asyncio.run(run_mcp_demo("mcp", flow="discover"))
    resource = asyncio.run(run_mcp_demo("resource", flow="resource"))
    prompt = asyncio.run(run_mcp_demo("prompt", flow="prompt"))
    tool = asyncio.run(run_mcp_demo("tool", flow="tool"))

    assert discover.flow == "discover"
    assert discover.resource_content == ""
    assert discover.prompt_text == ""
    assert discover.tool_result == ""

    assert "MCP resources expose read-only context" in resource.resource_content
    assert resource.prompt_text == ""
    assert resource.tool_result == ""

    assert prompt.resource_content == ""
    assert "MCP prompts package reusable instructions" in prompt.prompt_text
    assert prompt.tool_result == ""

    assert tool.resource_content == ""
    assert tool.prompt_text == ""
    assert "MCP tools are callable actions" in tool.tool_result


def test_ch10_mcp_demo_rejects_unknown_chapter():
    from agent_learning.mcp_demo import chapter_note, normalize_flow

    with pytest.raises(ValueError, match="unknown chapter"):
        chapter_note("unknown")

    with pytest.raises(ValueError, match="unknown MCP demo flow"):
        normalize_flow("unknown")


def test_ch11_react_agent_runs_reason_action_observation_loop():
    from agent_learning.llm.react_agent import ReActAgentInput, ReActAgentService

    service = ReActAgentService(FakeChatModel("unused"), [calculator_tool()])

    result = service.run(ReActAgentInput(question="12 * (7 + 3)"))

    assert result.answer == "12 * (7 + 3) = 120"
    assert [step.phase for step in result.steps] == [
        "reasoning",
        "action",
        "observation",
        "final",
    ]
    assert result.steps[1].name == "calculator"
    assert result.tool_messages
    assert result.tool_messages[0].name == "calculator"
    assert isinstance(result.messages[0], HumanMessage)
    assert isinstance(result.messages[2], ToolMessage)


def test_ch11_react_agent_rejects_blank_question():
    from agent_learning.llm.react_agent import ReActAgentInput, ReActAgentService

    service = ReActAgentService(FakeChatModel("unused"), [calculator_tool()])

    with pytest.raises(ValueError, match="question must not be blank"):
        service.run(ReActAgentInput(question="  "))


def test_ch11_example_uses_opt_in_provider_selection(monkeypatch, capsys):
    example = _load_example("ch11_react_agent.py")
    config = ModelProviderConfig(
        provider="openai",
        openai=OpenAIConfig(api_key="set", model="openai-test", base_url=""),
        anthropic=AnthropicConfig(api_key="", model="claude-test"),
    )

    def fake_select_chat_model(fake_response: str):
        return ExampleModelSelection("openai", FakeChatModel(fake_response), config, True)

    monkeypatch.setattr(example, "select_chat_model", fake_select_chat_model)
    monkeypatch.setattr(sys, "argv", ["ch11_react_agent.py", "12 * (7 + 3)"])

    example.main()

    output = capsys.readouterr().out
    assert "mode: openai" in output
    assert "provider: openai" in output
    assert "steps:" in output
    assert "final answer: 12 * (7 + 3) = 120" in output


def test_ch12_graph_tool_wraps_runnable_and_returns_json_ready_dict():
    from langchain_core.runnables import RunnableLambda

    from agent_learning.tools.graph_tool import graph_tool_from_runnable
    from agent_learning.llm.devops_triage import TriageInput

    tool = graph_tool_from_runnable(
        name="echo_triage",
        description="Echo a triage input through a runnable graph.",
        args_schema=TriageInput,
        runnable=RunnableLambda(lambda value: {**value, "severity": "low"}),
    )

    result = tool.invoke(
        {
            "symptom": "latency is slightly elevated",
            "service": "catalog",
            "environment": "staging",
        },
    )

    assert result == {
        "symptom": "latency is slightly elevated",
        "service": "catalog",
        "environment": "staging",
        "severity": "low",
    }


def test_ch12_graph_tool_rejects_missing_runnable():
    from agent_learning.tools.graph_tool import graph_tool_from_runnable
    from agent_learning.llm.devops_triage import TriageInput

    with pytest.raises(ValueError, match="runnable is required"):
        graph_tool_from_runnable(
            name="broken",
            description="Broken graph tool.",
            args_schema=TriageInput,
            runnable=None,
        )


def test_ch12_graph_tool_reports_runnable_errors():
    from langchain_core.runnables import RunnableLambda

    from agent_learning.tools.graph_tool import graph_tool_from_runnable
    from agent_learning.llm.devops_triage import TriageInput

    def fail(_value):
        raise RuntimeError("graph failed")

    tool = graph_tool_from_runnable(
        name="broken_triage",
        description="Broken triage graph.",
        args_schema=TriageInput,
        runnable=RunnableLambda(fail),
    )

    with pytest.raises(ValueError, match="runnable failed: graph failed"):
        tool.invoke(
            {
                "symptom": "checkout 500 errors increased",
                "service": "checkout",
                "environment": "prod",
            },
        )


def test_ch12_devops_triage_graph_generates_deterministic_actions():
    from agent_learning.llm.devops_triage import run_devops_triage

    result = run_devops_triage(
        {
            "symptom": "checkout 500 errors increased",
            "service": "checkout",
            "environment": "prod",
        },
    )

    assert result["severity"] == "high"
    assert result["suspected_area"] == "checkout application errors"
    assert result["next_actions"] == [
        "page the checkout on-call",
        "check recent checkout deploys in prod",
        "inspect prod checkout error logs",
        "prepare rollback if customer impact continues",
    ]
    assert "checkout" in result["summary"]


def test_ch12_graphtool_react_agent_calls_devops_triage_graph():
    from agent_learning.llm.devops_triage import devops_triage_tool
    from agent_learning.llm.react_agent import ReActAgentInput, ReActAgentService

    service = ReActAgentService(FakeChatModel("unused"), [devops_triage_tool()])

    result = service.run(
        ReActAgentInput(question="triage checkout 500 errors increased in prod"),
    )

    assert "severity high" in result.answer
    assert [step.phase for step in result.steps] == [
        "reasoning",
        "action",
        "observation",
        "final",
    ]
    assert result.steps[1].name == "devops_triage"
    assert result.tool_messages
    assert result.tool_messages[0].name == "devops_triage"


def test_ch13_incident_gate_approves_recommended_action_without_side_effects():
    from agent_learning.llm.human_in_loop import (
        IncidentApprovalDecision,
        IncidentApprovalInput,
        run_incident_approval_demo,
    )

    result = run_incident_approval_demo(
        IncidentApprovalInput(
            symptom="checkout 500 errors increased",
            service="checkout",
            environment="prod",
            recommended_action="page the checkout on-call",
        ),
        IncidentApprovalDecision(approved=True, reason="customer impact is confirmed"),
    )

    assert result.status == "approved"
    assert result.final_answer == "approved: page the checkout on-call for checkout in prod."
    assert result.interrupt_payload == {
        "question": "Approve this incident action?",
        "service": "checkout",
        "environment": "prod",
        "symptom": "checkout 500 errors increased",
        "recommended_action": "page the checkout on-call",
    }
    assert result.trace == [
        "graph -> approval_gate",
        "interrupt -> approval requested",
        "resume -> approved",
        "graph -> record_decision",
        "side_effects -> none",
    ]


def test_ch13_incident_gate_rejects_recommended_action_with_reason():
    from agent_learning.llm.human_in_loop import (
        IncidentApprovalDecision,
        IncidentApprovalInput,
        run_incident_approval_demo,
    )

    result = run_incident_approval_demo(
        IncidentApprovalInput(
            symptom="catalog latency is elevated",
            service="catalog",
            environment="staging",
            recommended_action="open an incident note",
        ),
        IncidentApprovalDecision(approved=False, reason="watch dashboards first"),
    )

    assert result.status == "rejected"
    assert result.final_answer == "rejected: open an incident note for catalog in staging. reason: watch dashboards first"
    assert "resume -> rejected" in result.trace
    assert result.decision_reason == "watch dashboards first"


def test_ch13_incident_gate_rejects_blank_inputs():
    from agent_learning.llm.human_in_loop import (
        IncidentApprovalDecision,
        IncidentApprovalInput,
        run_incident_approval_demo,
    )

    with pytest.raises(ValueError, match="symptom must not be blank"):
        run_incident_approval_demo(
            IncidentApprovalInput(
                symptom="  ",
                service="checkout",
                environment="prod",
                recommended_action="page the checkout on-call",
            ),
            IncidentApprovalDecision(approved=True, reason="confirmed"),
        )

    with pytest.raises(ValueError, match="recommended action must not be blank"):
        run_incident_approval_demo(
            IncidentApprovalInput(
                symptom="checkout 500 errors increased",
                service="checkout",
                environment="prod",
                recommended_action=" ",
            ),
            IncidentApprovalDecision(approved=True, reason="confirmed"),
        )


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
