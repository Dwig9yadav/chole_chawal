from typing import Dict, List

from backend.agent.llm import generate_completion
from backend.agent.tools import calculator, summarize_text, web_search


def _format_docs(docs: List[Dict]) -> str:
    if not docs:
        return "No RAG context available."

    lines = []
    for i, d in enumerate(docs, start=1):
        src = d.get("source", "unknown")
        page = d.get("page", "?")
        snippet = d.get("text", "")[:350]
        lines.append(f"[{i}] ({src}, page {page}) {snippet}")
    return "\n".join(lines)


def _pick_text_model(model_routing) -> str | None:
    if not model_routing:
        return None
    return (
        model_routing.reasoning_model
        or model_routing.text_model
        or model_routing.multilingual_model
        or model_routing.tool_model
    )


def run_agent(query: str, docs: List[Dict], model_routing=None) -> Dict:
    q_lower = query.lower()
    tool_calls: List[Dict] = []
    tool_context = ""

    if any(word in q_lower for word in ["calculate", "calc", "math", "+", "-", "*", "/"]):
        calc_out = calculator(query.replace("calculate", "").replace("calc", "").strip())
        tool_calls.append({"tool": "calculator", "output": calc_out})
        tool_context += f"\nCalculator: {calc_out}\n"

    if any(word in q_lower for word in ["search", "latest", "news", "best", "top", "web"]):
        search_out = web_search(query, max_results=4)
        tool_calls.append({"tool": "web_search", "output": search_out})
        tool_context += "\nWeb Search Results:\n"
        for i, item in enumerate(search_out, start=1):
            tool_context += f"{i}. {item.get('title')} - {item.get('snippet')} ({item.get('url')})\n"

    if "summarize" in q_lower and docs:
        joined = " ".join(d.get("text", "") for d in docs)
        summary = summarize_text(joined)
        tool_calls.append({"tool": "summarizer", "output": summary})
        tool_context += f"\nSummary Tool: {summary}\n"

    system_prompt = (
        "You are VoxAI, a Voice Study Assistant. "
        "Use RAG context first for factual study questions. "
        "If web search results are present, cite them briefly. "
        "Be clear, concise, and educational."
    )

    user_prompt = (
        f"User query: {query}\n\n"
        f"RAG context:\n{_format_docs(docs)}\n\n"
        f"Tool context:\n{tool_context or 'No external tool outputs.'}\n\n"
        "Answer in a student-friendly way with short bullet points when useful."
    )

    selected_model = _pick_text_model(model_routing)
    answer = generate_completion(system_prompt, user_prompt, model=selected_model)
    sources = [{"source": d.get("source"), "page": d.get("page")} for d in docs]

    return {
        "answer": answer,
        "sources": sources,
        "tool_calls": tool_calls,
        "models": {
            "selected_text_model": selected_model,
            "tool_model": getattr(model_routing, "tool_model", None),
            "vision_model": getattr(model_routing, "vision_model", None),
            "stt_model": getattr(model_routing, "stt_model", None),
            "tts_model": getattr(model_routing, "tts_model", None),
            "tts_voice": getattr(model_routing, "tts_voice", None),
        },
    }


def generate_quiz(topic: str, docs: List[Dict], model_routing=None) -> Dict:
    context = _format_docs(docs)
    system_prompt = "You are a quiz generator for college students."
    user_prompt = (
        f"Topic: {topic}\n"
        f"Context: {context}\n"
        "Create exactly 5 short quiz questions with concise answer key."
    )
    selected_model = _pick_text_model(model_routing)
    quiz_text = generate_completion(system_prompt, user_prompt, model=selected_model)
    return {
        "quiz": quiz_text,
        "models": {
            "selected_text_model": selected_model,
        },
    }
