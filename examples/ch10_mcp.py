from __future__ import annotations

import asyncio
import sys

from agent_learning.example_support import print_learning_sections
from agent_learning.mcp_demo import MCPDemoResult, run_mcp_demo


def main() -> None:
    chapter = " ".join(sys.argv[1:]) or "mcp"
    result = asyncio.run(run_mcp_demo(chapter))

    print("mode: local mcp stdio")
    print_learning_sections(
        goal="MCP server가 tool, resource, prompt를 노출하고 client가 표준 protocol로 호출하는 흐름을 봅니다.",
        happens=[
            "FastMCP server가 summarize_chapter tool, chapter resource template, review_chapter prompt를 등록합니다.",
            "stdio client가 server process를 시작하고 ClientSession.initialize()로 protocol handshake를 수행합니다.",
            "client는 list_tools, list_resource_templates, list_prompts로 capability를 발견한 뒤 resource/prompt/tool을 호출합니다.",
        ],
        matters="MCP를 사용하면 agent host가 특정 앱 코드에 직접 묶이지 않고 표준 protocol로 외부 capability를 발견하고 사용할 수 있습니다.",
        try_next=[
            '다른 primitive 설명을 읽어 보세요: uv run python examples/ch10_mcp.py tool',
            'resource 흐름만 보고 싶다면 chapter://mcp가 resource content로 어떻게 출력되는지 확인해 보세요.',
        ],
    )
    print_result(result)


def print_result(result: MCPDemoResult) -> None:
    print("server transport: stdio")
    print("available tools:")
    for name in result.tool_names:
        print(f"- {name}")
    print("available resources:")
    for template in result.resource_templates:
        print(f"- {template}")
    print("available prompts:")
    for name in result.prompt_names:
        print(f"- {name}")
    print(f"resource content: {result.resource_content}")
    print(f"prompt messages: {result.prompt_text}")
    print(f"tool result: {result.tool_result}")
    print(f"final answer: {result.final_answer}")


if __name__ == "__main__":
    main()
