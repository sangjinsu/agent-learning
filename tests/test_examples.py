from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_example(filename: str, *args: str) -> str:
    env = os.environ.copy()
    env["RUN_AGENT_LEARNING_INTEGRATION"] = "0"
    env["OPENAI_API_KEY"] = ""
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
    }

    friendly_sections = ["learning goal:", "what happens:", "why it matters:", "try next:"]

    for filename, expected_parts in examples.items():
        output = run_example(filename)
        for expected in [*friendly_sections, *expected_parts]:
            assert expected in output, f"{filename} output did not include {expected!r}:\n{output}"
