import ast
import operator as _op
import re
from typing import Any
from core.framework import Agent, ModelSettings, function_tool, Runner # Updated Import
import asyncio

# --- A safe arithmetic evaluator used by the calculator agent ---
_ALLOWED_OPS = {
    ast.Add: _op.add,
    ast.Sub: _op.sub,
    ast.Mult: _op.mul,
    ast.Div: _op.truediv,
    ast.Pow: _op.pow,
    ast.USub: _op.neg,
    ast.Mod: _op.mod,
}

def _eval_ast(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):        # type: ignore[attr-defined]
        return node.value
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval_ast(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval_ast(node.left), _eval_ast(node.right))
    raise ValueError("Unsupported expression")

@function_tool
def eval_expression(expression: str) -> str:
    """Safely evaluate an arithmetic expression using + - * / % ** and parentheses."""
    print(f"DEBUG: evaluating {expression}")
    expr = expression.strip().replace("^", "**")
    if not re.fullmatch(r"[\d\s\(\)\+\-\*/\.\^%]+", expr):
        return "Error: arithmetic only"
    try:
        tree = ast.parse(expr, mode="eval")
        return str(_eval_ast(tree.body))  # type: ignore[attr-defined]
    except Exception as e:
        return f"Error: {e}"

calculator_agent = Agent(
    name="Calculator",
    instructions=(
        "You are a precise calculator. "
        "When handed arithmetic, call the eval_expression tool and return only the final numeric result. "
        "No prose unless asked."
    ),
    tools=[eval_expression],
    model_settings=ModelSettings(temperature=0),
)

async def main():
    print("Testing Calculator Agent...")
    # Test case 1: Simple math
    result = await Runner.run(calculator_agent, "What is (12 * 5) + 3?")
    print(f"Final Answer: {result.final_output}\n")
    
    # Test case 2: Decimal math
    result = await Runner.run(calculator_agent, "Calculate 150 divided by 4")
    print(f"Final Answer: {result.final_output}\n")

if __name__ == "__main__":
    asyncio.run(main())
