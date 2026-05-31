from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping, Type

from langchain_core.tools import StructuredTool
from pydantic import BaseModel


def graph_tool_from_runnable(
    *,
    name: str,
    description: str,
    args_schema: Type[BaseModel],
    runnable: Any,
) -> StructuredTool:
    if runnable is None or not hasattr(runnable, "invoke"):
        raise ValueError("graph tool: runnable is required")

    def _run_graph_tool(**kwargs: Any) -> dict[str, Any]:
        model = args_schema(**kwargs)
        try:
            result = runnable.invoke(model.model_dump())
        except Exception as exc:
            raise ValueError(f"graph tool: runnable failed: {exc}") from exc
        return _json_ready_dict(result)

    return StructuredTool.from_function(
        func=_run_graph_tool,
        name=name,
        description=description,
        args_schema=args_schema,
    )


def _json_ready_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, BaseModel):
        return value.model_dump()
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    raise ValueError(f"graph tool: expected mapping output, got {type(value).__name__}")
