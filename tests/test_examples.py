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


def test_all_examples_print_detailed_learning_trace():
    examples = {
        "ch01_chatmodel.py": ["mode:", "question:", "prompt messages:", "final answer:"],
        "ch02_prompt_template.py": ["mode:", "input variables:", "formatted messages:"],
        "ch03_openai_chatmodel.py": ["mode:", "config:", "prompt messages:", "final answer:"],
        "ch04_tool_calling.py": ["mode:", "tool schema:", "model tool calls:", "tool messages:", "final answer:"],
        "ch05_chain.py": ["mode:", "input variables:", "prompt messages:", "model response:", "final answer:"],
        "ch06_graph.py": ["mode:", "graph:", "selected route:", "final answer:"],
        "ch07_streaming.py": ["mode:", "prompt messages:", "stream chunks:", "final answer:"],
        "ch08_callback_observability.py": ["mode:", "callback events:", "final answer:"],
        "ch09_rag.py": ["mode:", "loaded documents:", "retrieved sources:", "prompt context summary:", "final answer:"],
        "ch10_mcp.py": [
            "mode:",
            "mcp flow:",
            "target chapter:",
            "server transport:",
            "mcp call trace:",
            "client -> initialize",
            "available tools:",
            "available resources:",
            "available prompts:",
            "tool result:",
            "final answer:",
        ],
        "ch11_react_agent.py": [
            "mode:",
            "graph nodes:",
            "react steps:",
            "reasoning:",
            "action:",
            "observation:",
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

    for filename, expected_parts in examples.items():
        output = run_example(filename)
        for expected in [*friendly_sections, *expected_parts]:
            assert expected in output, f"{filename} output did not include {expected!r}:\n{output}"


def test_ch10_mcp_tool_mode_prints_actual_tool_call_trace():
    output = run_example("ch10_mcp.py", "tool")

    assert "mcp flow: tool" in output
    assert "target chapter: tool" in output
    assert "client -> call_tool name=summarize_chapter arguments={'chapter': 'tool'}" in output
    assert "server -> tool result:" in output
    assert "MCP tools are callable actions" in output
    assert "resource content:" not in output
    assert "prompt messages:" not in output
