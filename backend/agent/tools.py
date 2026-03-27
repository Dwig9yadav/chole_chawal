import ast
import operator
from typing import Dict, List


_SAFE_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

_SAFE_UNARY_OPS = {
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_expr(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_BIN_OPS:
        return _SAFE_BIN_OPS[type(node.op)](_eval_expr(node.left), _eval_expr(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_UNARY_OPS:
        return _SAFE_UNARY_OPS[type(node.op)](_eval_expr(node.operand))
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    try:
        parsed = ast.parse(expression, mode="eval")
        result = _eval_expr(parsed.body)
        return f"Result: {result}"
    except Exception as exc:
        return f"Calculator error: {exc}"


def web_search(query: str, max_results: int = 5) -> List[Dict]:
    try:
        from duckduckgo_search import DDGS

        items: List[Dict] = []
        with DDGS() as ddgs:
            for row in ddgs.text(query, max_results=max_results):
                items.append(
                    {
                        "title": row.get("title", ""),
                        "snippet": row.get("body", ""),
                        "url": row.get("href", ""),
                    }
                )
        return items
    except Exception:
        return []


def summarize_text(text: str, sentences: int = 3) -> str:
    clean = " ".join(text.split())
    if not clean:
        return "No content to summarize."

    # Simple extractive fallback summary.
    parts = [p.strip() for p in clean.split(".") if p.strip()]
    picked = parts[: max(1, sentences)]
    return ". ".join(picked) + ("." if picked else "")
