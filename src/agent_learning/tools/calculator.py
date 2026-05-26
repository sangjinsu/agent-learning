from __future__ import annotations

import ast
from dataclasses import asdict, dataclass

from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool


@dataclass(frozen=True)
class CalculatorOutput:
    expression: str
    result: float


class CalculatorInput(BaseModel):
    expression: str = Field(
        description="Arithmetic expression using +, -, *, /, and parentheses.",
    )


def calculate(expression: str) -> CalculatorOutput:
    cleaned = expression.strip()
    if not cleaned:
        raise ValueError("calculator tool: expression is required")
    try:
        parsed = ast.parse(cleaned, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"calculator tool: unsupported expression: {exc}") from exc
    return CalculatorOutput(expression=cleaned, result=_eval(parsed.body))


def calculator_tool() -> StructuredTool:
    return StructuredTool.from_function(
        func=_run_calculator_tool,
        name="calculator",
        description="Evaluate a safe arithmetic expression using +, -, *, /, and parentheses.",
        args_schema=CalculatorInput,
    )


def _run_calculator_tool(expression: str) -> dict[str, float | str]:
    return asdict(calculate(expression))


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _eval(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
        left = _eval(node.left)
        right = _eval(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if right == 0:
            raise ValueError("calculator tool: division by zero")
        return left / right
    raise ValueError(f"calculator tool: unsupported expression: {type(node).__name__}")
