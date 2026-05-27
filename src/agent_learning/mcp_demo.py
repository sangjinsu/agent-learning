from __future__ import annotations

import argparse
import asyncio
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server.fastmcp import FastMCP


CHAPTER_NOTES = {
    "mcp": (
        "Chapter 10 MCP explains Model Context Protocol as a standard way for hosts "
        "to discover and call server-provided tools, resources, and prompts."
    ),
    "tool": (
        "MCP tools are callable actions with structured input. They are useful when "
        "a host needs deterministic capabilities outside the model itself."
    ),
    "resource": (
        "MCP resources expose read-only context such as documents, records, or local "
        "notes that a host can browse and attach to a conversation."
    ),
    "prompt": (
        "MCP prompts package reusable instructions so a host can offer consistent "
        "workflows without copying prompt text into every client."
    ),
}


@dataclass(frozen=True)
class MCPDemoResult:
    tool_names: list[str]
    resource_templates: list[str]
    prompt_names: list[str]
    resource_content: str
    prompt_text: str
    tool_result: str
    final_answer: str


def chapter_note(chapter: str) -> str:
    key = chapter.strip().lower()
    if key not in CHAPTER_NOTES:
        raise ValueError(f"unknown chapter: {chapter}")
    return CHAPTER_NOTES[key]


def create_mcp_server() -> FastMCP:
    server = FastMCP("Agent Learning MCP")

    @server.tool()
    def summarize_chapter(chapter: str = "mcp") -> str:
        """Return a short learning summary for an agent-learning chapter."""
        note = chapter_note(chapter)
        return f"MCP connects hosts to external capabilities. {note}"

    @server.resource("chapter://{chapter}")
    def read_chapter(chapter: str) -> str:
        """Read a short chapter note as MCP resource content."""
        return chapter_note(chapter)

    @server.prompt()
    def review_chapter(chapter: str = "mcp") -> str:
        """Build a short review prompt for a chapter."""
        note = chapter_note(chapter)
        return f"Review Chapter 10 MCP. Explain this note in two concise bullets: {note}"

    return server


def run_server_stdio() -> None:
    create_mcp_server().run(transport="stdio")


async def run_mcp_demo(chapter: str = "mcp") -> MCPDemoResult:
    server_params = _server_parameters()
    with open(os.devnull, "w") as errlog:
        async with stdio_client(server_params, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools = await session.list_tools()
                resource_templates = await session.list_resource_templates()
                prompts = await session.list_prompts()

                resource = await session.read_resource(f"chapter://{chapter}")
                prompt = await session.get_prompt("review_chapter", arguments={"chapter": chapter})
                tool = await session.call_tool(
                    "summarize_chapter",
                    arguments={"chapter": chapter},
                )

                return MCPDemoResult(
                    tool_names=[tool_info.name for tool_info in tools.tools],
                    resource_templates=[
                        str(template.uriTemplate)
                        for template in resource_templates.resourceTemplates
                    ],
                    prompt_names=[prompt_info.name for prompt_info in prompts.prompts],
                    resource_content=_first_text(resource.contents),
                    prompt_text=_prompt_text(prompt.messages),
                    tool_result=_first_text(tool.content),
                    final_answer="MCP stdio demo completed.",
                )


def _server_parameters() -> StdioServerParameters:
    root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    src_path = str(root / "src")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        src_path
        if not existing_pythonpath
        else f"{src_path}{os.pathsep}{existing_pythonpath}"
    )
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "agent_learning.mcp_demo", "server"],
        env=env,
    )


def _first_text(contents: Iterable[object]) -> str:
    for content in contents:
        text = getattr(content, "text", None)
        if text is not None:
            return str(text)
    return ""


def _prompt_text(messages: Iterable[object]) -> str:
    parts: list[str] = []
    for message in messages:
        content = getattr(message, "content", None)
        text = getattr(content, "text", None)
        if text is not None:
            parts.append(str(text))
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Agent Learning MCP demo server")
    parser.add_argument("command", choices=["server"], help="Run the local MCP server over stdio")
    args = parser.parse_args(argv)
    if args.command == "server":
        run_server_stdio()


if __name__ == "__main__":
    main()
