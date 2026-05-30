from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_example(filename: str, *args: str) -> str:
    env = os.environ.copy()
    env["RUN_AGENT_LEARNING_INTEGRATION"] = "0"
    env["AGENT_LEARNING_PROVIDER"] = "openai"
    env["OPENAI_API_KEY"] = ""
    env["ANTHROPIC_API_KEY"] = ""
    completed = subprocess.run(
        [sys.executable, str(ROOT / "examples" / filename), *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout


def test_all_examples_print_concise_output_by_default():
    examples = {
        "ch01_chatmodel.py": ["chatmodel:", "mode:", "question:", "final answer:"],
        "ch02_prompt_template.py": ["prompt template:", "mode:", "message count:"],
        "ch03_openai_chatmodel.py": ["provider chatmodel:", "mode:", "provider:", "final answer:"],
        "ch04_tool_calling.py": ["tool calling:", "mode:", "tool:", "final answer:"],
        "ch05_chain.py": ["chain:", "mode:", "prompt message count:", "final answer:"],
        "ch06_graph.py": ["graph:", "mode:", "selected route:", "final answer:"],
        "ch07_streaming.py": ["streaming:", "mode:", "chunk count:", "final answer:"],
        "ch08_callback_observability.py": ["observability:", "mode:", "event count:", "final answer:"],
        "ch09_rag.py": ["rag:", "mode:", "retrieved sources:", "final answer:"],
        "ch10_mcp.py": [
            "mcp demo:",
            "mode:",
            "flow:",
            "final answer:",
        ],
        "ch11_react_agent.py": [
            "react agent:",
            "mode:",
            "steps:",
            "final answer:",
        ],
    }

    friendly_sections = [
        "learning goal:",
        "what happens:",
        "why it matters:",
        "try next:",
        "학습 목표:",
        "실행 흐름:",
        "중요한 이유:",
        "다음 실습:",
    ]

    verbose_only_sections = [
        *friendly_sections,
        "what happens:",
        "prompt messages:",
        "model response:",
        "mcp call trace:",
        "graph nodes:",
        "react steps:",
    ]

    for filename, expected_parts in examples.items():
        output = run_example(filename)
        for expected in expected_parts:
            assert expected in output, f"{filename} output did not include {expected!r}:\n{output}"
        for verbose_only in verbose_only_sections:
            assert verbose_only not in output, f"{filename} default output included verbose section {verbose_only!r}:\n{output}"


def test_all_examples_preserve_detailed_learning_trace_with_verbose():
    examples = {
        "ch01_chatmodel.py": ["prompt messages:", "final answer:"],
        "ch02_prompt_template.py": ["input variables:", "formatted messages:"],
        "ch03_openai_chatmodel.py": ["config:", "prompt messages:", "final answer:"],
        "ch04_tool_calling.py": ["tool schema:", "model tool calls:", "tool messages:", "final answer:"],
        "ch05_chain.py": ["input variables:", "model response:", "final answer:"],
        "ch06_graph.py": ["graph:", "model response:", "final answer:"],
        "ch07_streaming.py": ["stream chunks:", "final answer:"],
        "ch08_callback_observability.py": ["callback events:", "final answer:"],
        "ch09_rag.py": ["loaded documents:", "prompt context summary:", "prompt messages:", "final answer:"],
        "ch10_mcp.py": ["mcp call trace:", "available tools:", "tool result:", "final answer:"],
        "ch11_react_agent.py": ["graph nodes:", "react steps:", "observation:", "final answer:"],
    }

    friendly_sections = [
        "learning goal:",
        "what happens:",
        "why it matters:",
        "try next:",
        "학습 목표:",
        "실행 흐름:",
        "중요한 이유:",
        "다음 실습:",
    ]

    for filename, expected_parts in examples.items():
        output = run_example(filename, "--verbose")
        for expected in [*friendly_sections, *expected_parts]:
            assert expected in output, f"{filename} --verbose output did not include {expected!r}:\n{output}"


def test_ch10_mcp_tool_mode_prints_actual_tool_call_trace():
    output = run_example("ch10_mcp.py", "tool")

    assert "mcp demo:" in output
    assert "flow: tool" in output
    assert "target chapter: tool" in output
    assert "MCP tools are callable actions" in output
    assert "mcp call trace:" not in output
    assert "resource content:" not in output
    assert "prompt messages:" not in output


def test_ch10_mcp_tool_mode_verbose_prints_actual_tool_call_trace():
    output = run_example("ch10_mcp.py", "tool", "--verbose")

    assert "flow: tool" in output
    assert "client -> call_tool name=summarize_chapter arguments={'chapter': 'tool'}" in output
    assert "server -> tool result:" in output
    assert "tool result:" in output
