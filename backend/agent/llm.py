import os
from typing import Optional


def _openai_chat(system_prompt: str, user_prompt: str) -> Optional[str]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from openai import OpenAI

        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content or ""
    except Exception:
        return None


def generate_completion(system_prompt: str, user_prompt: str) -> str:
    response = _openai_chat(system_prompt, user_prompt)
    if response:
        return response

    # Offline-safe fallback for hackathon demos when API keys are absent.
    return (
        "I can still help, but no cloud LLM key is configured. "
        "Set OPENAI_API_KEY in backend/.env for full quality answers.\n\n"
        f"Your request was: {user_prompt[:350]}"
    )
